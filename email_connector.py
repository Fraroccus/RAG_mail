"""
Microsoft Graph API integration for Outlook email
"""

import os
import json
import requests
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication
import config


class EmailConnector:
    """Handle Outlook email operations via Microsoft Graph API"""
    
    def __init__(self):
        self.client_id = config.MS_CLIENT_ID
        self.client_secret = config.MS_CLIENT_SECRET
        self.tenant_id = config.MS_TENANT_ID
        self.redirect_uri = config.MS_REDIRECT_URI
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        
        self.app = ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self):
        """Get or refresh access token"""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            # Token typically expires in 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=result.get("expires_in", 3600) - 300)
            return self.access_token
        else:
            raise Exception(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
    
    def get_headers(self):
        """Get request headers with authorization"""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def fetch_unread_emails(self, max_results=10):
        """
        Fetch unread emails from inbox
        
        Args:
            max_results: Maximum number of emails to retrieve
        
        Returns:
            List of email dictionaries
        """
        endpoint = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"
        params = {
            "$filter": "isRead eq false",
            "$top": max_results,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,body,isRead,conversationId"
        }
        
        response = requests.get(endpoint, headers=self.get_headers(), params=params)
        
        if response.status_code == 200:
            data = response.json()
            emails = []
            
            for msg in data.get("value", []):
                email = {
                    "message_id": msg.get("id"),
                    "subject": msg.get("subject", ""),
                    "sender_email": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "sender_name": msg.get("from", {}).get("emailAddress", {}).get("name", ""),
                    "body": msg.get("body", {}).get("content", ""),
                    "body_type": msg.get("body", {}).get("contentType", "text"),
                    "received_date": msg.get("receivedDateTime"),
                    "conversation_id": msg.get("conversationId")
                }
                emails.append(email)
            
            return emails
        else:
            raise Exception(f"Failed to fetch emails: {response.status_code} - {response.text}")
    
    def send_email(self, to_email, subject, body, reply_to_message_id=None):
        """
        Send an email via Microsoft Graph API
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML supported)
            reply_to_message_id: Optional message ID to reply to
        
        Returns:
            True if sent successfully
        """
        if reply_to_message_id:
            # Send as reply
            endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{reply_to_message_id}/reply"
            payload = {
                "message": {
                    "body": {
                        "contentType": "HTML",
                        "content": body
                    }
                },
                "comment": ""
            }
        else:
            # Send new email
            endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
            payload = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": to_email
                            }
                        }
                    ]
                }
            }
        
        response = requests.post(endpoint, headers=self.get_headers(), json=payload)
        
        if response.status_code in [200, 201, 202]:
            return True
        else:
            raise Exception(f"Failed to send email: {response.status_code} - {response.text}")
    
    def mark_as_read(self, message_id):
        """Mark an email as read"""
        endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        payload = {"isRead": True}
        
        response = requests.patch(endpoint, headers=self.get_headers(), json=payload)
        
        return response.status_code == 200
    
    def get_email_by_id(self, message_id):
        """Retrieve a specific email by ID"""
        endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        
        response = requests.get(endpoint, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch email: {response.status_code} - {response.text}")
