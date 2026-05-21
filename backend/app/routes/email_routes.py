from fastapi import APIRouter

from app.services.email_service import (
    read_emails
)

router = APIRouter()


@router.get("/read-mails")
def trigger_mail_reading():

    read_emails()

    return {
        "message": "Emails processed successfully"
    }