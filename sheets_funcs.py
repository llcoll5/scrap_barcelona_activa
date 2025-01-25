from dotenv import load_dotenv
import os
import json

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

def get_credentials():
    google_credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    credentials_info = json.loads(google_credentials_json)
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    return gspread.authorize(credentials)

def get_worksheet(key, sheet_num=0):
    gc = get_credentials()
    sh = gc.open_by_key(key)
    return sh.get_worksheet(sheet_num)

def get_sheet_as_df(worksheet):
    return pd.DataFrame(worksheet.get_all_records())

def update_sheets(worksheet, dataframe):
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

def check_if_job_exists(dataframe, job, column="link"):
    return job not in set(dataframe[column])

def get_column_length(dataframe, column="link"):
    return len(dataframe.values.tolist())


_worksheet_key = "1jr4S3x7-8rHpTiFV0L9EtaYAqwg0n-2evUsoCiR6Jhg"
_worksheet = get_worksheet(_worksheet_key)


if __name__ == "__main__":
    
    dataframe = get_sheet_as_df(_worksheet)


    print(dataframe)

    print([dataframe.columns.values.tolist()] + dataframe.values.tolist())

    print(f"length values: {len(dataframe.values.tolist())}")

    dataframe.iloc[len(dataframe.values.tolist())] = ["testing", "link_Test"]

    print(f"checking if exists 'ee': {check_if_job_exists(dataframe, 'efe')}")


    update_sheets(_worksheet, dataframe)
