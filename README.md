# pollyanna-secret-santa

This project automates the process of sending personalized Pollyanna or Secret Santa emails using the Gmail API. Each participant receives an email detailing their assignments, with information about both their real and gag gifts. The emails are sent using the Gmail API with support for both plain text and HTML formats, with an optional embedded GIF in the HTML version.

## Features

- **Automated Email Sending**: Personalized Secret Santa emails are generated and sent to participants.
- **GIF Support**: Each email can include an optional GIF embedded in the HTML version.
- **OAuth 2.0 Authentication**: Secure authentication via Google's OAuth 2.0 system.

## Prerequisites

To run this project, you will need the following:

- **Python 3.10.7 or greater** installed on your system
- A Google account with access to Gmail
- A set of OAuth 2.0 credentials for accessing the Gmail API. See Setup Guide.
- Access to the Gmail API enabled in your Google Cloud Console. See Setup Guide.

## Setup Guide

Follow the steps below to configure the project and start sending emails:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/secret-santa-email-sender.git
cd secret-santa-email-sender
```

### 2. Build your Python Environment
Run the following command inside the cloned repository:
```bash
pipenv --python 3.10
pipenv sync
```

### 3. Follow the Quickstart Guide to enable Gmail API access.

Using your preferred Google Account, follow this [guide](https://developers.google.com/gmail/api/quickstart/python) to perform the following tasks:
* Create a Google Cloud Project
* [Enable the Gmail API](https://developers.google.com/gmail/api/quickstart/python#enable_the_api)
* [Configure the OAuth consetn screen](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen)
* [Authorize credentials for a desktop application](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)
* Add the `credentials.json` to the root direcotry of this repository.


### 4. Add a list of participants

Edit the `participatns.json` located in `pollyanna_secret_santa/resources/` with a JSON that matches the following structure:
```json
{
    "Participant One Name": "participant_one_email_address",
    "Participant Two Name": "participant_two_email_address",
    "Participant Three Name": "participant_three_email_address",
    ...
}
```

See below for a complete example:
```json
{
    "Shrek": "shrek@gmail.com",
    "Donkey": "donkey@hotmail.com",
    "Fiona": "fiona@yahoo.com"
}
```

### 5. (Optional) Add a GIF via environment variables
Should you choose, add an appropriate GIF to the email. You can do this by setting the GIF URL via an env variable as follows:
```bash
export GIF_URL="https://media.giphy.com/media/3ofT5EtPNBpIjC8jTy/giphy.gif" 
```

Alternatively, you can use the command line to pass in the GIF URL (see below).

### 6. Run the Program
After completing the above steps, you can run the program from the root directory as follows:
```bash
python pollyanna_secret_santa/main.py
```
or 
```bash
python pollyanna_secret_santa/main.py --gifUrl "https://media.giphy.com/media/3ofT5EtPNBpIjC8jTy/giphy.gif"
```
