import re
import json
import os
import requests

from groq import Groq

from msal import PublicClientApplication

from datetime import datetime

from dotenv import load_dotenv

from app.db.database import supabase

from app.services.employee_resolution_service import (
    resolve_employee
)


# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()


# ==========================================
# ENV VARIABLES
# ==========================================

CLIENT_ID = os.getenv(
    "CLIENT_ID"
)

TENANT_ID = os.getenv(
    "TENANT_ID"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


# ==========================================
# MICROSOFT AUTHORITY
# ==========================================

AUTHORITY = (

    f"https://login.microsoftonline.com/"
    f"{TENANT_ID}"
)


# ==========================================
# GRAPH SCOPES
# ==========================================

SCOPES = [

    "Mail.Read",

    "User.Read"
]


# ==========================================
# MSAL APP
# ==========================================

msal_app = PublicClientApplication(

    CLIENT_ID,

    authority=AUTHORITY
)


# ==========================================
# GROQ CLIENT
# ==========================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ==========================================
# GET ACCESS TOKEN
# ==========================================

def get_access_token():

    print(
        "\n========== OUTLOOK DEVICE LOGIN ==========\n"
    )

    flow = msal_app.initiate_device_flow(

        scopes=SCOPES
    )

    if "user_code" not in flow:

        raise Exception(
            "Failed to create device flow"
        )

    print(flow["message"])

    result = msal_app.acquire_token_by_device_flow(
        flow
    )

    if "access_token" not in result:

        raise Exception(
            "OUTLOOK LOGIN FAILED"
        )

    print(
        "\n========== LOGIN SUCCESS ==========\n"
    )

    return result["access_token"]


# ==========================================
# GET LAST SYNC TIME
# ==========================================

def get_last_sync_time():

    response = (

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

    data = response.data

    if len(data) == 0:

        return None

    return data[0]["last_sync_time"]


# ==========================================
# UPDATE LAST SYNC TIME
# ==========================================

def update_last_sync_time(

    sync_time,

    total_processed

):

    supabase.table(
        "mail_sync_tracker"
    ).insert({

        "last_sync_time":
            str(sync_time),

        "total_processed":
            total_processed

    }).execute()


# ==========================================
# GET QUARTER
# ==========================================

def get_quarter(date_obj):

    month = date_obj.month

    if month in [1, 2, 3]:

        return "Q1"

    elif month in [4, 5, 6]:

        return "Q2"

    elif month in [7, 8, 9]:

        return "Q3"

    else:

        return "Q4"


# ==========================================
# CLEAN JSON RESPONSE
# ==========================================

def extract_json_from_response(text):

    match = re.search(

        r'\[.*\]',

        text,

        re.DOTALL
    )

    if match:

        return match.group(0)

    return "[]"


# ==========================================
# FILTER VALID AWARD MAILS
# ==========================================

def is_award_mail(

    subject,

    body

):

    text = (

        f"{subject} {body}"
    ).lower()

    keywords = [

        "award",

        "nomination",

        "reward",

        "kudos",

        "skill seeker",

        "sentinel",

        "appreciation",

        "recognition",

        "learning",

        "technology",

        "ownership",

        "automation",

        "framework",

        "project"
    ]

    for keyword in keywords:

        if keyword in text:

            return True

    return False


# ==========================================
# CLASSIFY AWARD
# ==========================================

def classify_award(reason):

    reason = reason.lower()

    # ==========================================
    # SKILL SEEKER
    # ==========================================

    if (

        "learn" in reason

        or

        "technology" in reason

        or

        "upskill" in reason

        or

        "training" in reason

        or

        "new skill" in reason

        or

        "framework" in reason

        or

        "automation" in reason
    ):

        return "Skill Seeker Award"

    # ==========================================
    # SENTINEL
    # ==========================================

    if (

        "trust" in reason

        or

        "promise" in reason

        or

        "ownership" in reason

        or

        "consistency" in reason

        or

        "dependable" in reason
    ):

        return (
            "Sentinel of Small Promises Award"
        )

    # ==========================================
    # DEFAULT
    # ==========================================

    return "Kudos Award"


# ==========================================
# AI EXTRACTION
# ==========================================

def ai_extract_employee_data(body):

    prompt = f"""

Extract all employee award nominations from this mail.

STRICT RULES:

1. Return ONLY JSON
2. No explanation
3. No markdown
4. No extra text

JSON FORMAT:

[
  {{
    "employee_name": "",
    "employee_mail": "",
    "award_category": "",
    "project": "",
    "achievement_reason": "",
    "nominated_for": ""
  }}
]

Award categories:

- Kudos Award
- Skill Seeker Award
- Sentinel of Small Promises Award

Classification rules:

Kudos Award:
Given for excellent task completion.

Skill Seeker Award:
Given for learning new technology,
upskilling,
new tools,
new frameworks,
new technical capabilities.

Sentinel of Small Promises Award:
Given for trust,
ownership,
consistency,
keeping promises,
dependability.

If award category is NOT explicitly mentioned,
classify intelligently based on
achievement_reason.

MAIL:

{body}

"""

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.1
    )

    content = (

        response
        .choices[0]
        .message.content
    )

    print("\n========== RAW AI RESPONSE ==========\n")

    print(content)

    print("\n=====================================\n")

    cleaned_json = (

        extract_json_from_response(
            content
        )
    )

    print("\n========== CLEANED JSON ==========\n")

    print(cleaned_json)

    print("\n==================================\n")

    return json.loads(cleaned_json)


# ==========================================
# STORE MAIL DATA
# ==========================================

def store_mail_data(data):

    try:

        existing = (

            supabase
            .table("mail_data")

            .select("*")

            .eq(
                "employee_name",
                data["employee_name"]
            )

            .eq(
                "date_of_email",
                data["date_of_email"]
            )

            .execute()
        )

        if len(existing.data) > 0:

            print(
                "\n========== DUPLICATE SKIPPED ==========\n"
            )

            return None

        response = (

            supabase
            .table("mail_data")

            .insert(data)

            .execute()
        )

        print(
            "\n========== INSERT SUCCESS ==========\n"
        )

        print(response.data)

        print(
            "\n====================================\n"
        )

        return response.data

    except Exception as e:

        print(
            "\n========== INSERT ERROR ==========\n"
        )

        print(str(e))

        print(
            "\n==================================\n"
        )

        return None


# ==========================================
# READ OUTLOOK EMAILS
# ==========================================

def read_emails():

    try:

        print(
            "\n========== STARTING OUTLOOK MAIL READ ==========\n"
        )

        # ==========================================
        # ACCESS TOKEN
        # ==========================================

        access_token = (
            get_access_token()
        )

        headers = {

            "Authorization":

                f"Bearer {access_token}"
        }

        # ==========================================
        # LAST SYNC
        # ==========================================

        last_sync_time = get_last_sync_time()

        print(
            "\n========== LAST SYNC ==========\n"
        )

        print(last_sync_time)

        print(
            "\n================================\n"
        )

        # ==========================================
        # FETCH LATEST MAIL ONLY
        # ==========================================

        url = (

            "https://graph.microsoft.com/v1.0/"
            "me/mailFolders/inbox/messages"
            "?$top=1"
            "&$orderby=receivedDateTime DESC"
        )

        response = requests.get(

            url,

            headers=headers
        )

        data = response.json()

        print(
            "\n========== OUTLOOK RESPONSE ==========\n"
        )

        print(data)

        print(
            "\n======================================\n"
        )

        messages = data.get(
            "value",
            []
        )

        if len(messages) == 0:

            return {

                "success": True,

                "message":
                    "No mails found",

                "records": []
            }

        inserted_records = []

        processed_count = 0

        latest_mail_time = None

        # ==========================================
        # PROCESS MAILS
        # ==========================================

        for latest_mail in messages:

            # ==========================================
            # SUBJECT
            # ==========================================

            subject = latest_mail.get(
                "subject",
                ""
            )

            # ==========================================
            # HANDLE EMPTY SUBJECT
            # ==========================================

            if (

                subject is None

                or

                subject.strip() == ""
            ):

                subject = "NO SUBJECT"

            # ==========================================
            # BODY
            # ==========================================

            body_data = latest_mail.get(
                "body",
                {}
            )

            body = body_data.get(
                "content",
                ""
            )

            if not body:

                body = latest_mail.get(
                    "bodyPreview",
                    ""
                )

            # ==========================================
            # SKIP ONLY IF BOTH EMPTY
            # ==========================================

            if (

                subject == "NO SUBJECT"

                and

                body.strip() == ""
            ):

                print(
                    "\n========== EMPTY MAIL SKIPPED ==========\n"
                )

                continue

            # ==========================================
            # FILTER AWARD MAILS
            # ==========================================

            if not is_award_mail(

                subject,

                body
            ):

                print(
                    "\n========== NOT AWARD MAIL ==========\n"
                )

                print(subject)

                print(
                    "\n====================================\n"
                )

                continue

            print(
                "\n========== PROCESSING MAIL ==========\n"
            )

            print(subject)

            print(
                "\n=====================================\n"
            )

            # ==========================================
            # FROM EMAIL
            # ==========================================

            from_email = (

                latest_mail

                .get(
                    "from",
                    {}
                )

                .get(
                    "emailAddress",
                    {}
                )

                .get(
                    "address"
                )
            )

            # ==========================================
            # TO RECIPIENTS
            # ==========================================

            to_recipients = (

                latest_mail.get(
                    "toRecipients",
                    []
                )
            )

            to_email = ", ".join([

                recipient

                .get(
                    "emailAddress",
                    {}
                )

                .get(
                    "address"
                )

                for recipient in to_recipients
            ])

            # ==========================================
            # DATE
            # ==========================================

            parsed_date = datetime.fromisoformat(

                latest_mail.get(
                    "receivedDateTime"
                ).replace(
                    "Z",
                    "+00:00"
                )
            )

            latest_mail_time = parsed_date

            quarter = get_quarter(
                parsed_date
            )

            processed_count += 1

            print(
                "\n========== MAIL BODY ==========\n"
            )

            print(body)

            print(
                "\n===============================\n"
            )

            # ==========================================
            # AI EXTRACTION
            # ==========================================

            extracted_records = (

                ai_extract_employee_data(
                    body
                )
            )

            print(
                "\n========== AI EXTRACTED ==========\n"
            )

            print(extracted_records)

            print(
                "\n=================================\n"
            )

            # ==========================================
            # PROCESS EMPLOYEES
            # ==========================================

            for employee in extracted_records:

                if (

                    employee.get(
                        "employee_name"
                    ) == ""

                    and

                    employee.get(
                        "achievement_reason"
                    ) == ""
                ):

                    continue

                # ==========================================
                # TO EMAIL LIST
                # ==========================================

                to_email_list = [

                    recipient

                    .get(
                        "emailAddress",
                        {}
                    )

                    .get(
                        "address"
                    )

                    for recipient in to_recipients
                ]

                # ==========================================
                # EMPLOYEE RESOLUTION
                # ==========================================

                resolution = resolve_employee(

                    employee.get(
                        "employee_name"
                    ),

                    employee.get(
                        "employee_mail"
                    ),

                    to_email_list
                )

                print(
                    "\n========== EMPLOYEE RESOLUTION ==========\n"
                )

                print(resolution)

                print(
                    "\n=========================================\n"
                )

                resolved_employee = resolution.get(
                    "employee"
                )

                emp_id = None
                emp_name = None
                emp_mailid = None
                department = None

                if resolved_employee:

                    emp_id = (
                        resolved_employee["emp_id"]
                    )

                    emp_name = (
                        resolved_employee["emp_name"]
                    )

                    emp_mailid = (
                        resolved_employee["emp_mailid"]
                    )

                    department = (
                        resolved_employee["department"]
                    )

                else:

                    emp_name = employee.get(
                        "employee_name"
                    )

                # ==========================================
                # AWARD CATEGORY
                # ==========================================

                award_category = employee.get(
                    "award_category"
                )

                if (

                    award_category is None

                    or

                    award_category == ""
                ):

                    award_category = classify_award(

                        employee.get(
                            "achievement_reason",
                            ""
                        )
                    )

                # ==========================================
                # FINAL RECORD
                # ==========================================

                record = {

                    "employee_id":
                        emp_id,

                    "employee_name":
                        emp_name,

                    "employee_mailid":
                        emp_mailid,

                    "department":
                        department,

                    "award_category":
                        award_category,

                    "quarter":
                        quarter,

                    "nominated_by":
                        from_email,

                    "nominated_for":
                        employee.get(
                            "nominated_for"
                        ),

                    "project":
                        employee.get(
                            "project"
                        ),

                    "achievement_reason":
                        employee.get(
                            "achievement_reason"
                        ),

                    "date_of_email":
                        str(parsed_date),

                    "status":
                        "PENDING_APPROVAL",

                    "gift_card_code":
                        None,

                    "reference_id":
                        None,

                    "validity":
                        None,

                    "amount":
                        None,

                    "date_of_process":
                        None,

                    "voucher_status":
                        "NOT_ASSIGNED",

                    "reason_of_rejection":
                        None,

                    "from_email":
                        from_email,

                    "to_email":
                        to_email,

                    "subject":
                        subject,

                    "body":
                        body,

                    "certificate_generated":
                        False,

                    "mail_sent":
                        False,

                    "mail_status":
                        "NOT_SENT",

                    "match_type":
                        resolution.get(
                            "match_type"
                        ),

                    "match_confidence":
                        resolution.get(
                            "confidence"
                        ),

                    "resolution_status":
                        "PENDING_REVIEW"
                }

                print(
                    "\n========== INSERTING ==========\n"
                )

                print(record)

                print(
                    "\n===============================\n"
                )

                inserted = (

                    store_mail_data(
                        record
                    )
                )

                if inserted:

                    inserted_records.append(
                        inserted
                    )

        # ==========================================
        # UPDATE SYNC
        # ==========================================

        if latest_mail_time:

            update_last_sync_time(

                latest_mail_time,

                processed_count
            )

        print(
            "\n========== PROCESS COMPLETE ==========\n"
        )

        return {

            "success": True,

            "message":
                f"{len(inserted_records)} records inserted",

            "records":
                inserted_records
        }

    except Exception as e:

        print(
            "\n========== MAIN ERROR ==========\n"
        )

        print(str(e))

        print(
            "\n================================\n"
        )

        return {

            "success": False,

            "error":
                str(e)
        }