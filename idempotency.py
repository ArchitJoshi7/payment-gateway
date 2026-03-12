import threading

idempotency_store = {}
idempotency_lock = threading.Lock()
