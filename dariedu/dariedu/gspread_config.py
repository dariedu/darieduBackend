import os
import gspread
from dotenv import find_dotenv, load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv(find_dotenv())

SCOPES = os.getenv('SCOPES').split(',')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
SERVICE_ACCOUNT_FILE = '/app/credentials.json'  # for docker

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

gs = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
