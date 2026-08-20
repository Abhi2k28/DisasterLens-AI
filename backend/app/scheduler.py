from apscheduler.schedulers.background import BackgroundScheduler

from app.processor import process_demo_feed


scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        process_demo_feed,
        "interval",
        seconds=30,
        id="demo_feed_job",
        replace_existing=True
    )

    scheduler.start()
    print("Demo feed scheduler started")


def stop_scheduler():
    scheduler.shutdown()
    print("Demo feed scheduler stopped")