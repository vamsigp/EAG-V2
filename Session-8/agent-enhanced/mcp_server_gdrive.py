"""
MCP Server for Google Drive and Google Sheets Integration
Handles creating Google Sheets, sharing them, and getting shareable links
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import logging
from pathlib import Path

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Configuration
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials_sa.json")
GOOGLE_CREDENTIALS_BASE64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")  # Alternative: base64 encoded

# Initialize FastMCP
mcp = FastMCP("GoogleDrive")


def get_google_service(service_name: str, version: str = "v3"):
    """
    Get authenticated Google API service using service account credentials.
    
    Args:
        service_name: API service name (e.g., 'sheets', 'drive')
        version: API version (default: 'v3')
    
    Returns:
        Authenticated service object
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_path = Path(GOOGLE_SERVICE_ACCOUNT_JSON)
        
        # Handle base64 encoded credentials
        if GOOGLE_CREDENTIALS_BASE64:
            import base64
            import tempfile
            
            credentials_data = base64.b64decode(GOOGLE_CREDENTIALS_BASE64)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                f.write(credentials_data.decode('utf-8'))
                creds_path = Path(f.name)
        
        if not creds_path.exists():
            raise FileNotFoundError(
                f"Service account credentials not found at {creds_path}. "
                "Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_CREDENTIALS_BASE64"
            )
        
        credentials = service_account.Credentials.from_service_account_file(
            str(creds_path),
            scopes=SCOPES
        )
        
        service = build(service_name, version, credentials=credentials)
        logger.info(f"Authenticated Google {service_name} service")
        return service
        
    except Exception as e:
        logger.error(f"Error setting up Google service: {e}")
        raise


@mcp.tool()
async def create_spreadsheet(title: str, data_rows: List[List[str]]) -> str:
    """
    Create a new Google Spreadsheet with data and return the spreadsheet ID and URL.
    
    Args:
        title: Title/name for the spreadsheet
        data_rows: List of rows, where each row is a list of cell values
                   First row is treated as headers if provided
    
    Returns:
        JSON string with spreadsheet_id, spreadsheet_url, and sheet_id
    """
    try:
        sheets_service = get_google_service('sheets', 'v4')
        drive_service = get_google_service('drive', 'v3')
        
        # Create new spreadsheet
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        logger.info(f"Created spreadsheet: {title} (ID: {spreadsheet_id})")
        
        # Write data if provided
        if data_rows:
            # Prepare values for batch update
            body = {
                'values': data_rows
            }
            
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Wrote {len(data_rows)} rows to spreadsheet")
        
        result = {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': spreadsheet_url,
            'sheet_id': spreadsheet.get('sheets', [{}])[0].get('properties', {}).get('sheetId', 0)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating spreadsheet: {e}")
        return json.dumps({'error': str(e)}, indent=2)


@mcp.tool()
async def share_spreadsheet(spreadsheet_id: str, email: str, role: str = "reader") -> str:
    """
    Share a Google Spreadsheet with a specific email address.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet to share
        email: Email address to share with
        role: Permission level - 'reader', 'writer', or 'owner' (default: 'reader')
    
    Returns:
        Success message or error description
    """
    try:
        drive_service = get_google_service('drive', 'v3')
        
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission
        ).execute()
        
        logger.info(f"Shared spreadsheet {spreadsheet_id} with {email} as {role}")
        return f"Spreadsheet shared with {email} as {role}"
        
    except Exception as e:
        logger.error(f"Error sharing spreadsheet: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_spreadsheet_link(spreadsheet_id: str, make_public: bool = True) -> str:
    """
    Get the shareable link for a Google Spreadsheet.
    Optionally makes it publicly accessible.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        make_public: If True, makes the sheet publicly readable (default: True)
    
    Returns:
        Shareable URL string
    """
    try:
        drive_service = get_google_service('drive', 'v3')
        
        if make_public:
            # Make spreadsheet publicly readable
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission,
                fields='id'
            ).execute()
            
            logger.info(f"Made spreadsheet {spreadsheet_id} publicly readable")
        
        # Get file metadata to confirm URL
        file_metadata = drive_service.files().get(
            fileId=spreadsheet_id,
            fields='webViewLink'
        ).execute()
        
        url = file_metadata.get('webViewLink') or f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        logger.info(f"Got spreadsheet link: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Error getting spreadsheet link: {e}")
        # Return URL anyway (might still work)
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"


@mcp.tool()
async def append_to_spreadsheet(spreadsheet_id: str, range_name: str, values: List[List[str]]) -> str:
    """
    Append rows to an existing Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: A1 notation range (e.g., 'Sheet1!A1')
        values: List of rows to append
    
    Returns:
        Success message with number of cells updated
    """
    try:
        sheets_service = get_google_service('sheets', 'v4')
        
        body = {
            'values': values
        }
        
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        updated_cells = result.get('updates', {}).get('updatedCells', 0)
        logger.info(f"Appended {len(values)} rows to spreadsheet")
        
        return f"Appended {len(values)} rows. Updated {updated_cells} cells."
        
    except Exception as e:
        logger.error(f"Error appending to spreadsheet: {e}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Google Drive MCP Server")
    
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for development
    else:
        mcp.run(transport="stdio")  # Run with stdio transport

