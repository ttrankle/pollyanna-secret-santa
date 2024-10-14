"""Get the token credentials from the Google project"""

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.constants import GoogleAuthConstants

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def build_gmail_api_service():
    """
    Builds and returns a Gmail API service instance using OAuth 2.0 credentials.

    This function retrieves stored credentials from `token.json`, if available.
    If the credentials are expired or invalid, the user is prompted to log in and 
    new credentials are generated and saved. If no credentials are present, the user 
    is prompted to complete the OAuth 2.0 flow. The resulting credentials are used 
    to create a Gmail API service instance.

    Returns:
        googleapiclient.discovery.Resource: A Gmail API service instance.

    Raises:
        google.auth.exceptions.RefreshError: If the credentials cannot be refreshed.
        FileNotFoundError: If the client secrets file (`credentials.json`) is missing.
    
    Example:
        service = build_gmail_api_service()
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(GoogleAuthConstants.TOKEN_JSON):
        creds = Credentials.from_authorized_user_file(GoogleAuthConstants.TOKEN_JSON, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GoogleAuthConstants.CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(GoogleAuthConstants.TOKEN_JSON, "w") as token:
            token.write(creds.to_json())

    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)

    return service

