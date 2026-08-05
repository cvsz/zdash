import time

from app.workers.worker_service import run_once

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(2)
