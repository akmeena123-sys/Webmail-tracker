import logging
import os
import time
from datetime import datetime

from scraper import main as fetch_sheet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'scheduler.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

TARGET_TIMES = ['11:00', '17:00']


def run_if_due():
    now = datetime.now().strftime('%H:%M')
    if now in TARGET_TIMES:
        try:
            fetch_sheet()
            logging.info('Scraper ran at %s', now)
            print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Scraper ran at {now}')
        except Exception as exc:
            logging.exception('Scraper failed at %s', now)
            print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {exc}')


def main():
    print('Webmail tracker scheduler started.')
    print('It will refresh data at 11:00 and 17:00 every day.')
    print('Press Ctrl+C to stop it.')
    logging.info('Scheduler started')

    # Run immediately once after startup so data is available without waiting.
    try:
        fetch_sheet()
        logging.info('Initial scraper run performed on startup')
    except Exception as exc:
        logging.exception('Initial scraper run failed')
        print(f'Initial scraper run failed: {exc}')

    while True:
        run_if_due()
        time.sleep(60)


if __name__ == '__main__':
    main()
