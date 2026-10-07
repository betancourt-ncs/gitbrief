import logging
import requests
from formatters.slack_social import generate_social_brief
from formatters.slack_direct import generate_direct_brief
from slack import post_to_slack

logger = logging.getLogger(__name__)


# Social brief generation and delivery to Slack
def generate_and_post_social(parsed_data: dict, slack_social_url: str, delivery_id: str | None, tenant_id: int):
    try:
        brief = generate_social_brief(parsed_data)
    except Exception:
        # logs the actual type and full traceback
        logger.exception(
            f"Social brief generation failed | delivery_id={delivery_id} ; tenant_id={tenant_id}")
    else:
        if not brief:
            # OpenAI API request succeeded, but no text produced
            logger.error(
                f"Social brief generation returned empty output | delivery_id={delivery_id} ; tenant_id={tenant_id}")
        else:
            logger.info(
                f"Social brief generated | delivery_id={delivery_id} ; tenant_id={tenant_id}")
            try:
                post_to_slack(brief, slack_social_url)
                logger.info(
                    f"Social brief delivered to Slack | delivery_id={delivery_id} ; tenant_id={tenant_id}")
            # Unsuccessful responses (4xx or 5xx codes)
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else "unknown"
                logger.error(
                    f"Social brief delivery failed: Slack returned {status} | delivery_id={delivery_id} ; tenant_id={tenant_id}")
            # Timeouts and connection errors
            except requests.RequestException as e:
                logger.error(
                    f"Social brief delivery failed: {type(e).__name__} | delivery_id={delivery_id} ; tenant_id={tenant_id}")


# Direct brief generation and delivery to Slack
def generate_and_post_direct(parsed_data: dict, slack_direct_url: str, delivery_id: str | None, tenant_id: int):
    try:
        brief = generate_direct_brief(parsed_data)
    except Exception:
        logger.exception(
            f"Direct brief generation failed | delivery_id={delivery_id} ; tenant_id={tenant_id}")
    else:
        if not brief:
            logger.error(
                f"Direct brief generation returned empty output | delivery_id={delivery_id} ; tenant_id={tenant_id}")
        else:
            logger.info(
                f"Direct brief generated | delivery_id={delivery_id} ; tenant_id={tenant_id}")
            try:
                post_to_slack(brief, slack_direct_url)
                logger.info(
                    f"Direct brief delivered to Slack | delivery_id={delivery_id} ; tenant_id={tenant_id}")
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else "unknown"
                logger.error(
                    f"Direct brief delivery failed: Slack returned {status} | delivery_id={delivery_id} ; tenant_id={tenant_id}")
            except requests.RequestException as e:
                logger.error(
                    f"Direct brief delivery failed: {type(e).__name__} | delivery_id={delivery_id} ; tenant_id={tenant_id}")
