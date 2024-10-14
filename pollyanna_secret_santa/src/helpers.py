from typing import Dict

import json
from pathlib import Path
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.errors import HttpError

from src.constants import (
    HTML_CONTENT,
    MESSAGE_TEMPLATE,
    GoogleAuthConstants
)

from logging import getLogger

logger = getLogger(__name__)

def save_results_to_cache(results: Dict, cache_file_path: Path) -> None:
    """Save the results to a JSON file."""
    with open(cache_file_path, 'w') as file:
        json.dump(results, file)

def load_results_from_cache(cache_file_path: Path) -> Dict:
    """Load the prior year results from the JSON file, if it exists."""
    if cache_file_path.exists():
        logger.info("JSON from prior year exists. Loading...")
        return load_info_from_json(json_path=cache_file_path)
    
    logger.info("No prior year results")
    return {}

def load_info_from_json(json_path: Path) -> Dict:
    with open(json_path, 'r') as file:
        return json.load(file)

def create_html_content(name: str, gift_name: str, gag_name: str, gif_url: str = None) -> str:
    img_block = f'<p><img src="{gif_url}" alt="Christmas GIF" width="480" height="269"></p>' if gif_url else ""
    
    html_content = HTML_CONTENT.format(
        name=name, gift_name=gift_name, gag_name=gag_name, img_block=img_block
    )
    
    return html_content

def gmail_send_messages(service, participants, secret_santa_results, gif_url: str = None):
    """Create and send an email message with an embedded GIF.
    Print the returned message ID.
    Returns: Message object, including message ID.

    Load pre-authorized user credentials from the environment.
    TODO: See https://developers.google.com/identity for guides on implementing OAuth2.
    """
    for name, (gift_name, gag_name) in secret_santa_results.items():
        to_email = participants[name]
        try:
            # Create a multipart email message (HTML + Text)
            message = MIMEMultipart("alternative")

            # Text version (for non-HTML clients)
            text_content = MESSAGE_TEMPLATE.format(
                name=name, gift_name=gift_name, gag_name=gag_name
            )

            # HTML version with embedded GIF
            html_content = create_html_content(
                name=name, gift_name=gift_name, gag_name=gag_name, gif_url=gif_url
            )

            # Attach both plain text and HTML content
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))

            message["To"] = to_email
            message["From"] = "mclaughlintrankle@gmail.com"
            message["Subject"] = "SECRET EMAIL for SECRET SANTA! (2024)"

            # Encode the message in base64 for Gmail API
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}

            # Send the email message via the Gmail API
            send_message = (
                service.users().messages().send(userId="me", body=create_message).execute()
            )

            logger.info(f'Sent Message Id: {send_message["id"]} to {to_email}')
        except HttpError as error:
            logger.error(f"Error occured sending the email to {to_email}")
            send_message = None

def clean_up():
    files_to_remove = [GoogleAuthConstants.TOKEN_JSON]
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"Successfully removed {file_name}")
    