from datetime import datetime

from app.db.database import supabase


# ==========================================
# FETCH APPROVED EMPLOYEES
# ==========================================

def get_approved_employees():

    response = (

        supabase
        .table("mail_data")

        .select("*")

        .eq(
            "status",
            "APPROVED_PENDING_REWARD"
        )

        .is_(
            "reference_id",
            "null"
        )

        .execute()

    )

    return response.data


# ==========================================
# FETCH UNUSED VOUCHERS
# ==========================================

def get_unused_vouchers():

    response = (

        supabase
        .table("voucher_master")

        .select("*")

        .eq(
            "voucher_status",
            "UNUSED"
        )

        .execute()

    )

    return response.data


# ==========================================
# UPDATE EMPLOYEE WITH VOUCHER
# ==========================================

def update_employee_voucher(

    employee_id,

    voucher

):

    return (

        supabase
        .table("mail_data")

        .update({

            "gift_card_code":
                voucher["gift_card_code"],

            "reference_id":
                voucher["reference_id"],

            "validity":
                voucher["validity"],

            # ==========================================
            # FIXED INTEGER CONVERSION
            # ==========================================

            "amount":
                int(voucher["amount"]),

            "date_of_process":
                str(datetime.now()),

            "voucher_status":
                "ALLOCATED",

            "status":
                "READY_TO_SEND"

        })

        .eq(
            "id",
            employee_id
        )

        .execute()

    )


# ==========================================
# UPDATE VOUCHER STATUS
# ==========================================

def update_voucher_status(

    voucher_id

):

    return (

        supabase
        .table("voucher_master")

        .update({

            "voucher_status":
                "USED"

        })

        .eq(
            "id",
            voucher_id
        )

        .execute()

    )


# ==========================================
# MAIN ALLOCATION FUNCTION
# ==========================================

def allocate_vouchers():

    employees = (
        get_approved_employees()
    )

    vouchers = (
        get_unused_vouchers()
    )

    # ==========================================
    # NO EMPLOYEES
    # ==========================================

    if len(employees) == 0:

        return {

            "success": False,

            "message":
                "No approved employees found",

            "allocated_count": 0
        }

    # ==========================================
    # NO VOUCHERS
    # ==========================================

    if len(vouchers) == 0:

        return {

            "success": False,

            "message":
                "No unused vouchers available",

            "allocated_count": 0
        }

    # ==========================================
    # NOT ENOUGH VOUCHERS
    # ==========================================

    if len(vouchers) < len(employees):

        return {

            "success": False,

            "message":
                "Not enough vouchers available",

            "allocated_count": 0
        }

    allocated_count = 0

    # ==========================================
    # SEQUENTIAL ALLOCATION
    # ==========================================

    for i in range(len(employees)):

        employee = employees[i]

        voucher = vouchers[i]

        # ==========================================
        # UPDATE EMPLOYEE
        # ==========================================

        update_employee_voucher(

            employee["id"],

            voucher

        )

        # ==========================================
        # UPDATE VOUCHER
        # ==========================================

        update_voucher_status(

            voucher["id"]

        )

        allocated_count += 1

    return {

        "success": True,

        "message":
            "Voucher allocation completed",

        "allocated_count":
            allocated_count
    }