import pandas as pd

from backend.app.db.database import supabase


# ==========================================
# REQUIRED COLUMNS
# ==========================================

REQUIRED_COLUMNS = [

    "gift_card_code",

    "reference_id",

    "validity",

    "amount",

    "date_of_process",

    "voucher_status"
]


# ==========================================
# GET ALL VOUCHERS
# ==========================================

def get_all_vouchers():

    response = (

        supabase
        .table("voucher_master")

        .select("*")

        .order(
            "uploaded_at",
            desc=True
        )

        .execute()

    )

    return response.data


# ==========================================
# GET COUNTS
# ==========================================

def get_voucher_stats():

    all_vouchers = (
        supabase
        .table("voucher_master")
        .select("*")
        .execute()
    ).data

    total = len(all_vouchers)

    assigned = len([

        v for v in all_vouchers

        if v["voucher_status"] == "USED"

    ])

    unassigned = len([

        v for v in all_vouchers

        if v["voucher_status"] == "UNUSED"

    ])

    return {

        "total": total,

        "assigned": assigned,

        "unassigned": unassigned
    }


# ==========================================
# CHECK DUPLICATE
# ==========================================

def check_duplicate(reference_id):

    response = (

        supabase
        .table("voucher_master")

        .select("id")

        .eq(
            "reference_id",
            str(reference_id)
        )

        .execute()

    )

    return len(response.data) > 0


# ==========================================
# INSERT VOUCHER
# ==========================================

def insert_voucher(voucher):

    return (

        supabase
        .table("voucher_master")

        .insert(voucher)

        .execute()

    )


# ==========================================
# PROCESS FILE
# ==========================================

def process_voucher_file(df):

    inserted = 0

    duplicates = 0

    for _, row in df.iterrows():

        reference_id = str(
            row["reference_id"]
        )

        # ==========================================
        # DUPLICATE CHECK
        # ==========================================

        if check_duplicate(reference_id):

            duplicates += 1
            continue

        voucher_data = {

            "gift_card_code":
                row["gift_card_code"],

            "reference_id":
                reference_id,

            "validity":
                str(
                    pd.to_datetime(
                        row["validity"]
                    ).date()
                ),

            "amount":
                float(
                    row["amount"]
                ),

            "date_of_process":
                str(
                    pd.to_datetime(
                        row["date_of_process"]
                    ).date()
                ),

            "voucher_status":
                row["voucher_status"]
        }

        insert_voucher(
            voucher_data
        )

        inserted += 1

    return {

        "inserted": inserted,

        "duplicates": duplicates
    }