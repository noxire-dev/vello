import os
import re
from datetime import datetime

from vello.core.db import get_db, init_db
from vello.core.models import Recipient


def add_leads(csv_path, campaign_id):
    # Ensure DB is initialized
    init_db()

    check_email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    valid_emails = []

    print(f"Reading leads from {csv_path}...")

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            # Check if file has header, if so use csv.DictReader, else assume single column
            # For now, following user's simple line-by-line approach but safer
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Simple CSV handling: assume email is the first thing or the whole line
                parts = line.split(',')
                email = parts[0].strip()

                if re.match(check_email_regex, email):
                    valid_emails.append(email)
                else:
                    print(f"Skipping invalid email: {email}")
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        return

    if not valid_emails:
        print("No valid emails found.")
        return

    db = next(get_db())
    try:
        count = 0
        for email in valid_emails:
            # Check if already exists in this campaign to avoid unique constraint error
            existing = db.query(Recipient).filter_by(campaign_id=campaign_id, email=email).first()
            if existing:
                print(f"Skipping duplicate: {email}")
                continue

            recipient = Recipient(
                campaign_id=campaign_id,
                email=email,
                suppressed=False,
                created_at=datetime.utcnow()
            )
            db.add(recipient)
            count += 1

        db.commit()
        print(f"Successfully added {count} recipients to campaign {campaign_id}")

    except Exception as e:
        db.rollback()
        print(f"Error adding recipients: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Create a dummy csv if not exists for testing
    if not os.path.exists('leads.csv'):
        with open('leads.csv', 'w') as f:
            f.write("test1@example.com\n")
            f.write("test2@example.com\n")
            f.write("invalid-email\n")
        print("Created dummy leads.csv")

    # Default to campaign 1
    add_leads('leads.csv', 1)
