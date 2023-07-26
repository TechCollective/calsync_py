## Setup

1. Create a .env file and store it in the project directory. It should include the following AutoTask credentials, as well as Google credentials for the email alert email address, password, and recipient email address:

```
USERNAME =
SECRET=
APIINTEGRATIONCODE=
ALERTUSER =
ALERTPASS =
ALERTRECIPIENT =
TESTMODE = FALSE
```

2. Install pipenv and dependencies

3. Download credentials from Google Cloud, which can be found under OAuth 2.0 Client IDs. Save the file as credentials.json

4. From pipenv shell, run `python g_auth.py` and use the url to authenticate

5. From pipenv shell, run `python db_init.py` to initialize the database

6. From pipenv shell, run `python app.py`
