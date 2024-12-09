import os
import gspread
from dotenv import find_dotenv, load_dotenv
from google.oauth2.service_account import Credentials
from django.conf import settings

load_dotenv(find_dotenv())

SCOPES = os.getenv('SCOPES', '').split(',')
BASE_DIR = settings.BASE_DIR

SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

gs = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
