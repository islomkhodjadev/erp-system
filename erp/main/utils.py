import pandas as pd
import openpyxl


def extract_process_and_combine_sheets(excel_file, sheet_names):
    """
    Extracts specified sheets from an Excel file, processes the data (extracts code, name, packages, and price),
    reshapes the data, and performs price division by packages.

    Args:
        excel_file (str): Path to the Excel file.
        sheet_names (list): List of sheet names to extract.

    Returns:
        pd.DataFrame: Processed and reshaped DataFrame.
    """
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(excel_file, data_only=True)  # data_only=True gets calculated values
        combined_data = []

        # Extract data from sheets
        for sheet_name in sheet_names:
            if sheet_name not in workbook.sheetnames:
                continue

            # Read the sheet
            sheet = workbook[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(row)

            # Convert the sheet to a DataFrame
            df = pd.DataFrame(data)

            # Append to the combined data
            if not df.empty:
                combined_data.append(df)

        if not combined_data:
            return pd.DataFrame()  # Return an empty DataFrame if no valid data

        # Combine all DataFrames
        combined_df = pd.concat(combined_data, ignore_index=True, axis=0)

        # Extract the first 3, 4, or 5 digits (code) and the words after the digits (name)
        combined_df['code'] = combined_df[2].astype(str).str.extract(r'(\d{3,5})')
        combined_df['name'] = combined_df[2].astype(str).str.extract(r'(\D.*)')  # Extract the words after the number

        # Extract numeric values from columns 5 and 6
        combined_df['num_col_5'] = combined_df[5].astype(str).str.extract(r'(\d+)')
        combined_df['num_col_6'] = combined_df[6].astype(str).str.extract(r'(\d+)')

        # Combine numeric values from columns 5 and 6 into a new 'packages' column
        combined_df['packages'] = combined_df['num_col_5'].fillna('') + ' ' + combined_df['num_col_6'].fillna('')
        combined_df['packages'] = combined_df['packages'].str.strip()  # Remove extra spaces

        # Extract or assign the 'price' from column 7
        combined_df['price'] = combined_df[7].astype(str).str.extract(r'(\d+(\.\d+)?)')[0]  # Extract the first capturing group

        # Create a new DataFrame with 'code', 'name', 'packages', and 'price' columns
        new_df = combined_df[['code', 'name', 'packages', 'price']]

        # Group by 'code' and reshape
        grouped = new_df.groupby('code')

        # Create a list to store the reshaped rows
        reshaped_data = []

        for code, group in grouped:
            row = {"code": code}
            for idx, (_, row_data) in enumerate(group.iterrows(), start=2):  # Start index from 2
                if idx > 2:  # Skip writing the first row as `name_1`, `packages_1`, `price_1`
                    row[f"name_{idx-2}"] = row_data['name']
                    row[f"packages_{idx-2}"] = row_data['packages']
                    row[f"price_{idx-2}"] = row_data['price']  # Add the price for each row
            reshaped_data.append(row)

        # Convert the reshaped data into a new DataFrame
        final_df = pd.DataFrame(reshaped_data)

        # Loop through all columns starting with 'price_' and 'packages_' to perform the division
        for i in range(1, 7):  # Loop from 1 to 6 to handle price_1, ..., price_6
            price_column = f'price_{i}'
            packages_column = f'packages_{i}'

            # Ensure both price and packages columns are numeric for division
            final_df[price_column] = pd.to_numeric(final_df[price_column], errors='coerce')
            final_df[packages_column] = pd.to_numeric(final_df[packages_column], errors='coerce')

            # Perform the division and update the price column
            final_df[price_column] = final_df[price_column] / final_df[packages_column]

        # Return the processed DataFrame
        return final_df

    except FileNotFoundError:
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    except Exception as e:
        return pd.DataFrame()  # Return an empty DataFrame in case of error




import os
import django
import sys
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Use your bot token from .env
API_TOKEN = os.getenv("tg_token")



def send_message_to_user(user_id, message):
    """
    Function to send a message to a user via Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    data = {
        'chat_id': user_id,
        'text': message
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code != 200:
        return f"Failed to send message. Status code: {response.status_code}"
    else:
        return f"Message sent to user {user_id}"