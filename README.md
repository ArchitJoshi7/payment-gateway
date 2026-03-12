# IdemPay — Idempotency Simulator

A live payment gateway simulator that demonstrates idempotent transaction design.
Fire duplicate requests, watch the middleware block them in real time, and see
exactly one charge hit the ledger — every time.

---

## What It Demonstrates

- Idempotency key lifecycle: `new → processing → completed`
- Concurrent duplicate blocking via threading lock
- Database-level safety via `UNIQUE` constraint on `idempotency_key`
- Real-time middleware log and transaction ledger

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | SQLite + SQLAlchemy |
| Concurrency | Python `threading.Lock` |
| Frontend | Vanilla JS + Chart.js |
| Server | Uvicorn |

---

## Getting Started
```bash
# 1. Clone the repo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload

# 4. Open the dashboard
http://127.0.0.1:8000
```

---

## Try It

- **Buy $150 Apple Stock** — single charge with a fresh idempotency key
- **Panic Double-Click (×5)** — 5 simultaneous requests with the same key
  → Expect 1 success, 4 conflicts (409)
- Run until balance < $150 to trigger insufficient funds (402)

---

## Project Structure
```
idempay/
├── main.py           # App bootstrap, startup seeding
├── api.py            # /charge, /ledger, /log endpoints
├── db.py             # SQLAlchemy engine + session
├── models.py         # User and Transaction ORM models
├── idempotency.py    # In-memory store + threading lock
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

---

## License

MIT
