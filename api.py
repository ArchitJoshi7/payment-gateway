import asyncio
import json
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User, Transaction
from idempotency import idempotency_store, idempotency_lock

router = APIRouter()

@router.get("/ledger")
def get_ledger():
    db = SessionLocal()
    user = db.query(User).first()
    txs = db.query(Transaction).order_by(Transaction.timestamp.desc()).all()
    db.close()
    return {"user": {"name": user.name, "balance": user.balance}, "transactions": [
        {"id": t.id, "amount": t.amount, "idempotency_key": t.idempotency_key, "timestamp": t.timestamp.isoformat()} for t in txs
    ]}

@router.get("/log")
def get_log(request: Request):
    if not hasattr(request.app.state, "log"): request.app.state.log = []
    return {"log": request.app.state.log[-30:]}

@router.post("/charge")
async def charge(request: Request, idempotency_key: str = Header(None)):
    if not hasattr(request.app.state, "log"): request.app.state.log = []
    log = request.app.state.log
    log.append(f"Received charge with key: {idempotency_key}")
    if not idempotency_key:
        raise HTTPException(400, "Missing Idempotency-Key header")
    with idempotency_lock:
        status = idempotency_store.get(idempotency_key)
        if status:
            if status["status"] == "processing":
                log.append(f"409 Conflict: {idempotency_key} still processing")
                raise HTTPException(409, "Duplicate in progress")
            if status["status"] == "completed":
                log.append(f"200 OK: {idempotency_key} already completed")
                return JSONResponse(status_code=200, content=status["data"])
        idempotency_store[idempotency_key] = {"status": "processing"}
        log.append(f"Locked {idempotency_key} for processing")
    await asyncio.sleep(2)
    db = SessionLocal()
    user = db.query(User).first()
    if user.balance < 150:
        db.close()
        with idempotency_lock:
            idempotency_store.pop(idempotency_key, None)
        log.append(f"402 Payment Required: Insufficient funds for {idempotency_key}")
        raise HTTPException(402, "Insufficient funds")
    user.balance -= 150
    tx = Transaction(user_id=user.id, amount=150, idempotency_key=idempotency_key)
    db.add(tx)
    db.commit()
    db.refresh(user)
    db.close()
    payload = {"message": "Charged $150 for Apple Stock", "balance": user.balance}
    with idempotency_lock:
        idempotency_store[idempotency_key] = {"status": "completed", "data": payload}
    log.append(f"200 OK: {idempotency_key} completed, balance now {user.balance}")
    return payload
