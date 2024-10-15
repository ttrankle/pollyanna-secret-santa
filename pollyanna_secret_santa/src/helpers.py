from typing import Dict

import json
from pathlib import Path
import os
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.errors import HttpError

from src.constants import (
    HTML_CONTENT,
    MESSAGE_TEMPLATE,
    GoogleAuthConstants,
    REGULAR,
    GAG
)

from logging import getLogger

logger = getLogger(__name__)


class YearAllocator:
    
    YEAR = datetime.now().year


class SantasMemory:

    def __init__(self, cached_results: dict, memory_length: int = 3):
        years_to_load = [str(YearAllocator.YEAR - i) for i in range(1, memory_length + 1)]
        
        past_regular_gift_assignments = {}
        past_gag_gift_assignments = {}
        
        for year in years_to_load:
            years_assignment: dict = cached_results.get(year)

            if years_assignment is not None:
                regular_assignment = years_assignment.get(REGULAR)
                for gift_giver in regular_assignment:
                    gift_receiver = regular_assignment[gift_giver]
                    past_regular_gift_assignments[gift_giver] = past_regular_gift_assignments.get(gift_giver, set())
                    past_regular_gift_assignments[gift_giver].add(gift_receiver)

                gag_assignment = years_assignment.get(GAG, [])
                for gift_giver in gag_assignment:
                    gift_receiver = gag_assignment[gift_giver]
                    past_gag_gift_assignments[gift_giver] = past_gag_gift_assignments.get(gift_giver, set())
                    past_gag_gift_assignments[gift_giver].add(gift_receiver)

        self.past_regular_gift_assignments = past_regular_gift_assignments
        self.past_gag_gift_assignments = past_gag_gift_assignments

    def get_past_regular_gift_recievers(self, participants_name: str) -> set:
        return self.past_regular_gift_assignments.get(participants_name, set())

    def get_past_gag_gift_recievers(self, participants_name: str) -> set:
        return self.past_gag_gift_assignments.get(participants_name, set())


def save_results_to_cache(prior_year_results: Dict, results: Dict, cache_file_path: Path) -> None:
    """
    Save the results dictionary to a JSON file.

    This function takes a dictionary of results and saves it to the specified 
    file path in JSON format. If the file already exists, it will be overwritten.

    Args:
        results (Dict): The dictionary containing the results to be cached.
        cache_file_path (Path): The file path where the results will be saved.

    Returns:
        None

    Example:
        results = {"status": "success", "data": [1, 2, 3]}
        save_results_to_cache(results, Path("/path/to/cache.json"))
    """
    prior_year_results[YearAllocator.YEAR] = results

    with open(cache_file_path, 'w') as file:
        json.dump(prior_year_results, file, indent=4)


def load_results_from_cache(cache_file_path: Path) -> Dict:
    """
    Load the prior year results from the specified JSON file, if it exists.

    This function attempts to load results from a JSON file at the given file path. 
    If the file exists, it logs the event and returns the results as a dictionary. 
    If the file does not exist, an empty dictionary is returned.

    Args:
        cache_file_path (Path): The file path where the cached results are stored.

    Returns:
        Dict: A dictionary containing the cached results, or an empty dictionary if the file does not exist.

    Example:
        results = load_results_from_cache(Path("/path/to/cache.json"))
    
    Logs:
        - Info level log is generated if the file exists or not.
    """
    if cache_file_path.exists():
        logger.info("JSON from prior year exists. Loading...")
        return load_info_from_json(json_path=cache_file_path)
    
    logger.info("No prior year results")
    return {}


def load_info_from_json(json_path: Path) -> Dict:
    """
    Load and return data from a JSON file.

    This function reads the contents of a JSON file at the specified path and 
    returns it as a dictionary.

    Args:
        json_path (Path): The path to the JSON file to be loaded.

    Returns:
        Dict: A dictionary containing the data from the JSON file.

    Raises:
        FileNotFoundError: If the specified JSON file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.

    Example:
        data = load_info_from_json(Path("/path/to/data.json"))
    """
    with open(json_path, 'r') as file:
        return json.load(file)


def create_html_content(name: str, gift_name: str, gag_name: str, gif_url: str = None) -> str:
    """
    Create and return an HTML content string using the provided name, gift, gag, and optional GIF URL.

    This function generates an HTML content string by formatting predefined HTML with the provided
    name, gift name, gag gift name, and an optional GIF image URL. If the GIF URL is provided, an 
    image block will be included in the HTML; otherwise, no image will be included.

    Args:
        name (str): The recipient's name to be included in the HTML content.
        gift_name (str): The name of the primary gift.
        gag_name (str): The name of the gag gift.
        gif_url (str, optional): The URL for a GIF image to be embedded in the HTML content. 
                                 Defaults to None.

    Returns:
        str: The formatted HTML content as a string.

    Example:
        html = create_html_content(
            name="John", 
            gift_name="Smartwatch", 
            gag_name="Rubber Chicken", 
            gif_url="https://example.com/image.gif"
        )
    """
    img_block = f'<p><img src="{gif_url}" alt="Christmas GIF" width="480" height="269"></p>' if gif_url else ""
    
    html_content = HTML_CONTENT.format(
        name=name, gift_name=gift_name, gag_name=gag_name, img_block=img_block
    )
    
    return html_content


def gmail_send_messages(service, participants, secret_santa_results, gif_url: str = None) -> None:
    """
    Create and send an email message with an embedded GIF to participants of Secret Santa.

    This function iterates through the `secret_santa_results` to create and send personalized 
    Secret Santa emails to the participants. Each email contains both a plain text and HTML 
    version (with an optional GIF) and is sent via the Gmail API.

    Args:
        service: The Gmail API service instance used to send the email.
        participants (Dict[str, str]): A dictionary mapping participant names to their email addresses.
        secret_santa_results (Dict[str, Tuple[str, str]]): A dictionary containing the participant's name 
            as the key and a tuple of gift name and gag gift name as the value.
        gif_url (str, optional): The URL of a GIF image to be embedded in the HTML version of the email. 
                                 Defaults to None.

    Returns:
        None

    Raises:
        googleapiclient.errors.HttpError: If an error occurs while sending the email via the Gmail API.

    Example:
        gmail_send_messages(service, participants, secret_santa_results, gif_url="https://example.com/gif.gif")

    Logs:
        - Info level log for each successfully sent email (including the message ID and recipient email).
        - Error level log if sending the email fails for any recipient.
    """
    the_year = datetime.now().year
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
            message["Subject"] = f"SECRET EMAIL for SECRET SANTA! ({the_year})"

            # Encode the message in base64 for Gmail API
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}

            # Send the email message via the Gmail API
            send_message = (
                service.users().messages().send(userId="me", body=create_message).execute()
            )

            logger.info(f'Sent Message Id: {send_message["id"]} to {to_email}')
        except HttpError as error:
            logger.error(f"Error occurred sending the email to {to_email}")
            send_message = None


def clean_up() -> None:
    """
    Remove specified files from the system, if they exist.

    This function checks for the existence of specific files (e.g., OAuth tokens) and 
    removes them if found. A log entry is created for each successfully removed file.

    Files removed:
        - `TOKEN_JSON`: The OAuth token JSON file used for authentication.

    Returns:
        None

    Example:
        clean_up()  # Removes the token.json file and logs the event.
    
    Logs:
        - Info level log is generated for each file that is successfully removed.
    """
    files_to_remove = [GoogleAuthConstants.TOKEN_JSON]
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"Successfully removed {file_name}")

    