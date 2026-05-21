from difflib import get_close_matches

from app.db.database import supabase


# ==========================================
# GET ALL EMPLOYEES
# ==========================================

def get_all_employees():

    response = (

        supabase
        .table("employee_master")

        .select("*")

        .execute()
    )

    return response.data


# ==========================================
# EXACT EMAIL MATCH
# ==========================================

def exact_email_match(

    email_id
):

    if not email_id:

        return None

    response = (

        supabase
        .table("employee_master")

        .select("*")

        .eq(
            "emp_mailid",
            email_id
        )

        .execute()
    )

    data = response.data

    if len(data) == 0:

        return None

    return {

        "employee":
            data[0],

        "match_type":
            "EXACT_EMAIL",

        "confidence":
            100
    }


# ==========================================
# EXACT NAME MATCH
# ==========================================

def exact_name_match(

    emp_name
):

    if not emp_name:

        return None

    response = (

        supabase
        .table("employee_master")

        .select("*")

        .ilike(
            "emp_name",
            emp_name
        )

        .execute()
    )

    data = response.data

    if len(data) == 0:

        return None

    return {

        "employee":
            data[0],

        "match_type":
            "EXACT_NAME",

        "confidence":
            95
    }


# ==========================================
# FUZZY NAME MATCH
# ==========================================

def fuzzy_name_match(

    emp_name
):

    if not emp_name:

        return None

    employees = get_all_employees()

    all_names = [

        emp["emp_name"]

        for emp in employees
    ]

    matches = get_close_matches(

        emp_name,

        all_names,

        n=1,

        cutoff=0.75
    )

    if len(matches) == 0:

        return None

    matched_name = matches[0]

    for emp in employees:

        if emp["emp_name"] == matched_name:

            return {

                "employee":
                    emp,

                "match_type":
                    "FUZZY_NAME",

                "confidence":
                    80
            }

    return None


# ==========================================
# RESOLVE EMPLOYEE
# ==========================================

def resolve_employee(

    employee_name,

    employee_mail,

    to_emails=None
):

    # ==========================================
    # 1. EXACT MAIL MATCH
    # ==========================================

    result = exact_email_match(
        employee_mail
    )

    if result:

        return result

    # ==========================================
    # 2. TO RECIPIENT MATCH
    # ==========================================

    if to_emails:

        for mail in to_emails:

            result = exact_email_match(
                mail
            )

            if result:

                result["match_type"] = (
                    "TO_RECIPIENT_MATCH"
                )

                result["confidence"] = 90

                return result

    # ==========================================
    # 3. EXACT NAME MATCH
    # ==========================================

    result = exact_name_match(
        employee_name
    )

    if result:

        return result

    # ==========================================
    # 4. FUZZY MATCH
    # ==========================================

    result = fuzzy_name_match(
        employee_name
    )

    if result:

        return result

    # ==========================================
    # 5. NO MATCH
    # ==========================================

    return {

        "employee": None,

        "match_type":
            "UNRESOLVED",

        "confidence":
            0
    }