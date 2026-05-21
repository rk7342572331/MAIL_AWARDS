from app.db.database import supabase


# ==========================================
# FETCH PENDING APPROVALS
# ==========================================

def get_pending_approvals():

    response = (

        supabase
        .table("mail_data")

        .select("*")

        .eq(
            "status",
            "PENDING_APPROVAL"
        )

        .order(
            "date_of_email",
            desc=True
        )

        .execute()

    )

    return response.data


# ==========================================
# APPROVE EMPLOYEE
# ==========================================

def approve_employee(record_id):

    response = (

        supabase
        .table("mail_data")

        .update({

            "status":
                "APPROVED_PENDING_REWARD"

        })

        .eq(
            "id",
            record_id
        )

        .execute()

    )

    return response.data


# ==========================================
# REJECT EMPLOYEE
# ==========================================

def reject_employee(

    record_id,

    rejection_reason

):

    response = (

        supabase
        .table("mail_data")

        .update({

            "status":
                "REJECTED",

            "reason_of_rejection":
                rejection_reason

        })

        .eq(
            "id",
            record_id
        )

        .execute()

    )

    return response.data