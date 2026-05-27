from app.workers.worker_service import run_once
import time

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(2)
