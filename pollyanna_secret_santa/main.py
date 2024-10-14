import os
import argparse
import json
from pathlib import Path
import logging

from src.secret_santa import generate_secret_santa_results
from src.helpers import (
    clean_up,
    gmail_send_messages,
    load_info_from_json,
    load_results_from_cache,
    save_results_to_cache,
)

from src.auth import build_gmail_api_service

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] — %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

PARTICIPATNS_JSON_RELATIVE_PATH = "resources/participants.json"
CACHE_FILE_RELATIVE_PATH = "resources/prior_year_santa_results.json"


def parse_args():
    """
    Parse the command line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--gifUrl',
        type=str,
        help='A URL to a GIF you want to include at the end of the email.',
        required=False,
        default=None
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    parent_path = Path(__file__).parent
    path_to_participatns_json = Path(parent_path, PARTICIPATNS_JSON_RELATIVE_PATH)

    # Load the participants for this year
    try:
        participants = load_info_from_json(path_to_participatns_json)
    except json.decoder.JSONDecodeError as json_error:
        raise NotImplementedError(
            f"Please populate a JSON with the following key: value pairs as name: email in {path_to_participatns_json}"
        )

    logger.info("Participatns loaded from participants.json")

    # Load prior year results from cache, or use a hardcoded fallback
    cache_results_path = Path(parent_path, CACHE_FILE_RELATIVE_PATH)
    prior_year_results = load_results_from_cache(cache_results_path)

    # Generate Secret Santa results
    secret_santa_results = generate_secret_santa_results(
        participants, prior_year_results
    )

    # Define the GIF URL and use it in an HTML <img> tag
    gif_url = os.getenv("GIF_URL", args.gifUrl)

    # Send out emails
    service = build_gmail_api_service()
    gmail_send_messages(
        service=service,
        participants=participants,
        secret_santa_results=secret_santa_results,
        gif_url=gif_url,
    )

    # Cache the results for future use
    save_results_to_cache(
        results=secret_santa_results, cache_file_path=cache_results_path
    )

    clean_up()
