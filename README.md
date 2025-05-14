
# Email to Issue Script Documentation

## Overview

This script processes unread emails from an email inbox and creates GitHub issues based on the contents of the emails. It automatically handles attachments, extracts email subjects, sender information, and cleans email bodies by removing signatures. The script labels the issues according to predefined labels mapped to keywords in the email subject.

---

## Prerequisites

- **Python 3.10 or higher**
- **GitHub Account and Personal Access Token** with appropriate permissions to create issues in a repository.
- **An Email Account** that supports IMAP (e.g., Gmail, Outlook, etc.) and allows access via IMAP.
- **Required Python Libraries** (listed below)

---

## Installation Steps

### 1. Clone the Repository

Clone the repository containing the script to your local machine or server:

```bash
git clone https://github.com/yourusername/email-to-github-issue.git
cd email-to-github-issue
```

### 2. Set up Python Environment

Create and activate a Python virtual environment to avoid conflicts with other Python projects:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scriptsctivate`
```

### 3. Install Required Dependencies

Install the necessary Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests`
- `python-dotenv`
- `imaplib`
- `email`
- `re`
- `talon` (for signature extraction, optional)
- `logging`

### 4. Configure Environment Variables

Create a `.env` file at the root of the project directory with the following configurations:

```env
IMAP_SERVER=your.imap.server.com
EMAIL_ACCOUNT=your-email@example.com
EMAIL_PASSWORD=your-email-password
GITHUB_REPO=your-username/your-repository
GITHUB_TOKEN=your-github-personal-access-token
```

- **IMAP_SERVER**: Your email provider's IMAP server (e.g., `imap.gmail.com` for Gmail).
- **EMAIL_ACCOUNT**: Your email address used for fetching emails.
- **EMAIL_PASSWORD**: Your email password or application-specific password.
- **GITHUB_REPO**: The GitHub repository in which issues will be created (e.g., `username/repo`).
- **GITHUB_TOKEN**: A personal access token generated in GitHub to authenticate and create issues.

### 5. Configure Label Map

The script allows you to map keywords from email subjects to GitHub issue labels. You can configure the `LABEL_MAP` in the `.env` file or modify it directly in the script:

```env
LABEL_MAP="[configure]:configure,[edit]:edit,[invalid]:invalid,[question]:question,[write post]:write-post"
```

Each key-value pair in `LABEL_MAP` should be separated by commas. The key is the subject keyword (e.g., "[configure]") and the value is the corresponding GitHub label (e.g., "configure").

### 6. Configure Signature Cleaning Triggers

The script supports cleaning email signatures. By default, it removes common signature patterns (like "Best regards," "Thanks," etc.). You can extend these patterns by adding custom triggers in the `signature_triggers.txt` file:

```signature_triggers.txt
(?i)^best regards
(?i)^kind regards
(?i)^thanks
(?i)^regards
(?i)^sincerely
(?i)^cheers
(?i)^--$
(?i)^sent from my
(?i)^email:
(?i)^internet:
(?i)^[a-zA-Z\s]{2,30}$
(?i)administrator|manager|engineer|director|coordinator|officer|developer|consultant
```

### 7. Configure Logging

The script logs its actions (like issue creation) in a file named `email_to_issue.log`. Logs will include information about the status of each issue creation, errors, and attachments.

---

## Running the Script

### 1. Run the Script

Execute the script using Python:

```bash
python email-to-issue.py
```

The script will:
- Fetch unread emails from the configured inbox.
- Process the subject and body to clean up signatures and extract relevant information.
- Create GitHub issues using the GitHub API and attach files from the email (if any).

### 2. Monitor the Log File

Check the `email_to_issue.log` file for logs related to issue creation, including any errors or issues that might have occurred during execution.

---

## Error Handling

The script provides logging for any errors encountered. Common errors could include:
- **IMAP login failure**: Incorrect email credentials.
- **GitHub API error**: Incorrect token or repository permissions.
- **Signature extraction issues**: If no valid signatures are found or extraction fails.

You can check the log file for more details on errors and take appropriate action.

---

## Customization

### Adding More Label Mapping

To add more labels or keywords, simply update the `LABEL_MAP` in the `.env` file. Each new entry should follow the format `"[label_keyword]": "label_value"`. After saving the changes, rerun the script for it to pick up the new mappings.

### Custom Signature Extraction

You can extend the signature cleaning functionality by modifying the regular expressions in the `clean_signature_fallback` function.

---

## Troubleshooting

- **Issue: Emails not being marked as read.**
  - Check if your email provider allows IMAP access and that you’ve granted the script the necessary permissions to read the emails.
  
- **Issue: GitHub issues not created.**
  - Verify that the GitHub token has the required permissions to create issues in the specified repository.

---
