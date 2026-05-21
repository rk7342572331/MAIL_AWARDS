from fastapi import APIRouter

from app.services.mail_sender_service import (

    fetch_mail_ready_records,

    send_single_mail

)

from app.db.database import supabase


router = APIRouter()


# ==========================================
# GET MAIL READY RECORDS
# ==========================================

@router.get(
    "/mail-ready"
)

def get_mail_ready():

    return fetch_mail_ready_records()


# ==========================================
# SEND MAIL USING DB ID
# ==========================================

@router.post(
    "/send-mail/{mail_id}"
)

def send_mail(

    mail_id: int

):

    response = (

        supabase
        .table("mail_data")

        .select("*")

        .eq(
            "id",
            mail_id
        )

        .single()

        .execute()

    )

    employee = response.data

    if not employee:

        return {

            "success": False,

            "message":
                "Employee record not found"
        }

    return send_single_mail(
        employee
    )