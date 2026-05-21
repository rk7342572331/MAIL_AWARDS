from fastapi import APIRouter

from app.db.database import supabase

from app.services.email_service import (
    read_emails
)


router = APIRouter()


# ==========================================
# READ MAILS
# ==========================================

@router.post(
    "/trigger-mail-read"
)

def trigger_mail_read():

    return read_emails()


# ==========================================
# DASHBOARD STATS
# ==========================================

@router.get(
    "/dashboard-stats"
)

def dashboard_stats():

    all_records = (

        supabase
        .table("mail_data")

        .select("*")

        .execute()
    )

    data = all_records.data

    total_records = len(data)

    pending_approval = len([

        x for x in data

        if x.get("status")
        == "PENDING_APPROVAL"
    ])

    approved = len([

        x for x in data

        if x.get("status")
        == "READY_TO_SEND"
    ])

    certificates_generated = len([

        x for x in data

        if x.get("certificate_generated")
        is True
    ])

    mail_sent = len([

        x for x in data

        if x.get("mail_sent")
        is True
    ])

    # ==========================================
    # LAST SYNC
    # ==========================================

    sync_response = (

        supabase
        .table("mail_sync_tracker")

        .select("*")

        .order(
            "id",
            desc=True
        )

        .limit(1)

        .execute()
    )

    sync_data = sync_response.data

    last_sync = None

    if len(sync_data) > 0:

        last_sync = sync_data[0].get(
            "last_sync_time"
        )

    return {

        "total_records":
            total_records,

        "pending_approval":
            pending_approval,

        "approved":
            approved,

        "certificates_generated":
            certificates_generated,

        "mail_sent":
            mail_sent,

        "last_sync":
            last_sync
    }