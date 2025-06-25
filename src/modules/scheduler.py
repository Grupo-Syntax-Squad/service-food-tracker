import threading
import time
import schedule
from sqlalchemy.orm import Session

from src.database import DatabaseConnection
from src.modules.log import Log
from src.modules.scheduled_feeding import ScheduledFeedingManager

db_conn = DatabaseConnection()


def job() -> None:
    Log().info("Iniciando ScheduleFeedingManager")
    session: Session = db_conn.create_session()
    try:
        manager = ScheduledFeedingManager(session)
        manager.execute()
    finally:
        session.close()


def start_scheduler() -> None:
    Log().info("Iniciando agendador")
    schedule.every(1).minutes.do(job)

    def run_scheduler() -> None:
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
