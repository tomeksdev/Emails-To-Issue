# Author: Tomo Novak(Vujca)
# Mail: info@tomeksdev.com
# Website: https://tomeksdev.com
# GitHUB project: https://github.com/tomeksdev/Emails-To-Issue
# GitHUB Issue: https://github.com/tomeksdev/Emails-To-Issue/issues

import os
import imaplib
import email
import requests
from dotenv import load_dotenv
import re
import logging

# Load environment variables
load_dotenv(".env")

# Logging setup
LOG_FILE = 'email_to_issue.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Load LABEL_MAP from .env file
def load_label_map():
    label_map = {}
    label_map_str = os.getenv("LABEL_MAP")
    if label_map_str:
        label_pairs = label_map_str.split(",")
        for pair in label_pairs:
            key, value = pair.split(":")
            label_map[key.strip()] = value.strip()
    return label_map

LABEL_MAP = load_label_map()

# Load signature triggers from a separate file
def load_signature_triggers(file_path="signature_triggers.txt"):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Extract labels from subject
def extract_labels(subject):
    labels = []
    for key, label in LABEL_MAP.items():
        if key.lower() in subject.lower():
            labels.append(label)
    return labels or ["review"]

# Remove label keywords from subject line
def clean_subject(subject):
    cleaned = subject
    for key in LABEL_MAP.keys():
        cleaned = re.sub(re.escape(key), '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

# Clean the email body by removing signature using dynamic triggers
def clean_signature_fallback(body, signature_triggers):
    lines = body.strip().splitlines()
    cleaned_lines = []
    signature_started = False

    for i, line in enumerate(lines):
        if any(re.search(pattern, line.strip()) for pattern in signature_triggers):
            signature_started = True
        if not signature_started:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()

# Read unread emails
def fetch_unread_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select('inbox')
    status, messages = mail.search(None, '(UNSEEN)')
    email_ids = messages[0].split()
    emails = []

    for e_id in email_ids:
        status, data = mail.fetch(e_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        subject = msg['subject'] or "No Subject"
        sender = msg['from']
        body = ""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    body += part.get_payload(decode=True).decode(errors='ignore')
                elif 'attachment' in content_disposition:
                    filename = part.get_filename()
                    content = part.get_payload(decode=True)
                    attachments.append((filename, content))
        else:
            body += msg.get_payload(decode=True).decode(errors='ignore')

        emails.append((subject.strip(), body.strip(), sender.strip(), attachments))

    mail.logout()
    return emails

# Upload file to GitHub Gist
def upload_attachment_to_gist(filename, content):
    url = "https://api.github.com/gists"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "description": f"Attachment: {filename}",
        "public": False,
        "files": {
            filename: {"content": content.decode(errors="ignore")}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()["files"][filename]["raw_url"]
    return None

# Create GitHub issue
def create_github_issue(title, body, sender, attachments, labels):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/issues'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    attachment_links = ""
    for filename, content in attachments:
        link = upload_attachment_to_gist(filename, content)
        if link:
            attachment_links += f"\n📎 [{filename}]({link})"

    issue_body = f"{body}\n\n---\n**Reported by:** {sender}\n{attachment_links}"

    data = {
        'title': title,
        'body': issue_body,
        'labels': labels
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()

# Parse sender name/email
def parse_sender(sender):
    match = re.match(r'(.*)<(.*)>', sender)
    if match:
        name = match.group(1).strip().strip('"') or "Unknown"
        email_addr = match.group(2).strip()
    else:
        name = sender
        email_addr = sender
    return f"{name} | {email_addr}"

# Main logic
def run():
    try:
        # Load signature triggers from the file
        signature_triggers = load_signature_triggers()

        emails = fetch_unread_emails()
        logger.info(f"Fetched {len(emails)} unread emails.")

        for subject, body, sender, attachments in emails:
            labels = extract_labels(subject)
            clean_subj = clean_subject(subject)
            body_no_sig = clean_signature_fallback(body, signature_triggers)
            title = f"[{parse_sender(sender)}] {clean_subj}"

            logger.info(f"Creating issue for email: {subject} from {sender}")
            status, res = create_github_issue(title, body_no_sig, sender, attachments, labels)

            if status == 201:
                logger.info(f"Issue created successfully: {res.get('html_url')}")
            else:
                logger.error(f"Failed to create issue: {res.get('message')}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    logger.info("Script started.")
    run()
    logger.info("Script finished.")