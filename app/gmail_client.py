import base64
import email.utils
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]


@dataclass
class GmailMessage:
    message_id: str
    thread_id: str
    sender_email: str
    sender_name: str | None
    subject: str
    body: str


class GmailClient:
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._build_service()

    def _build_service(self):
        creds = None

        if Path(self.token_path).exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                SCOPES,
            )

            try:
                creds = flow.run_local_server(port=0)
            except Exception:
                print("")
                print("Could not open a browser on this machine.")
                print("Use the authorization URL below, approve access, then paste the code here.")
                print("")
                creds = flow.run_console()
            
            Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def ensure_label(self, label_name: str) -> str:
        labels = self.service.users().labels().list(userId="me").execute().get("labels", [])

        for label in labels:
            if label["name"] == label_name:
                return label["id"]

        created = (
            self.service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )

        return created["id"]

    def search_message_ids(self, query: str, max_results: int = 10) -> list[str]:
        response = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )

        return [m["id"] for m in response.get("messages", [])]

    def get_message(self, message_id: str) -> GmailMessage:
        raw = (
            self.service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

        payload = raw.get("payload", {})
        headers = payload.get("headers", [])

        subject = self._header(headers, "Subject") or ""
        from_raw = self._header(headers, "From") or ""
        sender_name, sender_email = email.utils.parseaddr(from_raw)

        body = self._extract_body(payload)

        return GmailMessage(
            message_id=message_id,
            thread_id=raw.get("threadId", ""),
            sender_email=sender_email.lower().strip(),
            sender_name=sender_name or None,
            subject=subject,
            body=body,
        )

    def add_label(self, message_id: str, label_name: str) -> None:
        label_id = self.ensure_label(label_name)

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_id]},
        ).execute()

    def send_email(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> None:
        message = email.message.EmailMessage()
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        payload = {"raw": encoded}

        if thread_id:
            payload["threadId"] = thread_id

        self.service.users().messages().send(
            userId="me",
            body=payload,
        ).execute()

    @staticmethod
    def _header(headers: list[dict], name: str) -> str | None:
        for header in headers:
            if header.get("name", "").lower() == name.lower():
                return header.get("value")
        return None

    def _extract_body(self, payload: dict) -> str:
        parts = payload.get("parts")

        if not parts:
            return self._decode_part(payload)

        plain_parts = []
        html_parts = []

        def walk(part):
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                plain_parts.append(self._decode_part(part))
            elif mime_type == "text/html":
                html_parts.append(self._html_to_text(self._decode_part(part)))

            for child in part.get("parts", []) or []:
                walk(child)

        for part in parts:
            walk(part)

        if plain_parts:
            return "\n".join([p for p in plain_parts if p]).strip()

        return "\n".join([h for h in html_parts if h]).strip()

    @staticmethod
    def _decode_part(part: dict) -> str:
        data = part.get("body", {}).get("data")
        if not data:
            return ""

        decoded = base64.urlsafe_b64decode(data.encode("utf-8"))
        return decoded.decode("utf-8", errors="replace")

    @staticmethod
    def _html_to_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n").strip()