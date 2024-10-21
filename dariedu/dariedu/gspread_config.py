import os
import gspread
from google.oauth2.service_account import Credentials


SCOPES = os.getenv('SCOPES').split(',')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

gs = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
