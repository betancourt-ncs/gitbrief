import logging
import os
from dotenv import load_dotenv

from scripts.send_webhook import parsed_data
from briefing import generate_and_post_social

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

if __name__ == "__main__":
    generate_and_post_social(
        parsed_data,
        os.environ["SLACK_WEBHOOK_URL"],
        "test-delivery-001",
        0,
    )
