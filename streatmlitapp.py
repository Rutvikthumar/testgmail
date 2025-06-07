import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    token_file = 'token.pickle'
    
    # Load existing credentials
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If no (valid) credentials available, prompt login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def search_emails(service, subject_text):
    results = service.users().messages().list(
        userId='me',
        q=f'subject:{subject_text}'
    ).execute()
    messages = results.get('messages', [])
    return messages

# Streamlit UI
st.title("📧 Gmail Subject Search")

if st.button("Authenticate with Gmail"):
    try:
        service = authenticate_gmail()
        st.success("✅ Authenticated successfully.")
    except Exception as e:
        st.error(f"❌ Authentication failed: {e}")

if 'service' not in st.session_state and os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
        st.session_state['service'] = build('gmail', 'v1', credentials=creds)

if 'service' in st.session_state:
    subject = st.text_input("Enter subject to search:")
    if subject:
        msgs = search_emails(st.session_state['service'], subject)
        st.write(f"Found {len(msgs)} emails.")
        for msg in msgs[:5]:  # Preview first 5
            st.write(f"ID: {msg['id']}")
