import os

import base64

import requests

from mimetypes import guess_type

from datetime import datetime

from pathlib import Path

from dotenv import load_dotenv

from msal import PublicClientApplication

from app.db.database import supabase


# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()


# ==========================================
# BASE DIR
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


# ==========================================
# MAIL ASSETS
# ==========================================

BANNER_IMAGE = (

    BASE_DIR

    / "backend"

    / "mail_assets"

    / "banner.png"
)

GIFT_IMAGE = (

    BASE_DIR

    / "backend"

    / "mail_assets"

    / "gift.png"
)

LOGO_IMAGE = (

    BASE_DIR

    / "backend"

    / "mail_assets"

    / "logo.png"
)


# ==========================================
# OUTLOOK CONFIG
# ==========================================

CLIENT_ID = os.getenv(
    "CLIENT_ID"
)

TENANT_ID = os.getenv(
    "TENANT_ID"
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

    "Mail.Send",

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
# GET ACCESS TOKEN
# ==========================================

def get_access_token():

    print(
        "\n========== OUTLOOK LOGIN ==========\n"
    )

    result = (

        msal_app.acquire_token_interactive(

            scopes=SCOPES
        )
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
# FETCH MAIL READY RECORDS
# ==========================================

def fetch_mail_ready_records():

    response = (

        supabase
        .table("mail_data")

        .select("*")

        .eq(
            "certificate_generated",
            True
        )

        .eq(
            "mail_sent",
            False
        )

        .execute()
    )

    return response.data


# ==========================================
# GENERATE SUBJECT
# ==========================================

def generate_subject(employee):

    return (

        f"Congratulations "
        f"{employee['employee_name']} "
        f"on Receiving "
        f"{employee['award_category']}"
    )


# ==========================================
# GENERATE HTML BODY
# ==========================================

def generate_html_body(employee):

    employee_name = employee[
        "employee_name"
    ]

    award = employee[
        "award_category"
    ]

    reference_id = employee.get(
        "reference_id",
        "-"
    )

    gift_code = employee.get(
        "gift_card_code",
        "-"
    )

    validity = employee.get(
        "validity",
        "-"
    )

    amount = employee.get(
        "amount",
        "-"
    )

    html = f"""

    <html>

    <body
        style="
            font-family: Arial;
            background-color: white;
            padding: 20px;
        "
    >

    <div
        style="
            width: 100%;
            text-align: center;
        "
    >

    <img
        src="cid:banner"
        width="100%"
    >

    </div>

    <br>

    <p
        style="
            font-size: 18px;
        "
    >

    Dear <b>{employee_name}</b>,

    </p>

    <p
        style="
            font-size: 16px;
            line-height: 1.7;
        "
    >

    On behalf of the entire team of Ganit,
    we would like to express our admiration.

    The work you have done signifies
    new capabilities for Ganit —
    the endless dedication you have shown
    in your work,
    and the professionalism
    you have exhibited
    have not gone unnoticed;
    you are an inspiration
    to every fellow Ganitan.

    </p>

    <p
        style="
            font-size: 16px;
        "
    >

    Please find attached your
    <b>{award}</b> certificate.

    </p>

    <br>

    <table
        border="1"
        cellpadding="10"
        cellspacing="0"
        style="
            border-collapse: collapse;
            width: 450px;
            font-size: 15px;
        "
    >

        <tr>
            <td><b>Gift Card Code</b></td>
            <td>{gift_code}</td>
        </tr>

        <tr>
            <td><b>Reference ID</b></td>
            <td>{reference_id}</td>
        </tr>

        <tr>
            <td><b>Validity</b></td>
            <td>{validity}</td>
        </tr>

        <tr>
            <td><b>Voucher Amount</b></td>
            <td>₹ {amount}</td>
        </tr>

    </table>

    <br><br>

    <img
        src="cid:gift"
        width="220"
    >

    <br><br>

    <img
        src="cid:logo"
        width="180"
    >

    <br><br>

    <p
        style="
            font-size: 15px;
        "
    >

    Thanks,<br><br>

    Charulatha M<br>

    +91 6369588217<br>

    www.ganitinc.com

    </p>

    </body>

    </html>

    """

    return html


# ==========================================
# CREATE INLINE IMAGE ATTACHMENT
# ==========================================

def create_inline_attachment(

    image_path,

    content_id

):

    with open(

        image_path,

        "rb"

    ) as image_file:

        encoded_string = base64.b64encode(

            image_file.read()

        ).decode("utf-8")

    mime_type, _ = guess_type(
        image_path
    )

    return {

        "@odata.type":

            "#microsoft.graph.fileAttachment",

        "name":
            Path(image_path).name,

        "contentType":
            mime_type,

        "contentBytes":
            encoded_string,

        "isInline":
            True,

        "contentId":
            content_id
    }


# ==========================================
# SEND SINGLE MAIL
# ==========================================

def send_single_mail(

    employee,

    custom_subject=None,

    custom_body=None

):

    try:

        # ==========================================
        # RECIPIENT
        # ==========================================

        recipient = employee.get(
            "employee_mailid"
        )

        if not recipient:

            return {

                "success": False,

                "message":
                    "Employee mail ID missing"
            }

        # ==========================================
        # SUBJECT
        # ==========================================

        subject = (

            custom_subject

            if custom_subject

            else generate_subject(
                employee
            )
        )

        # ==========================================
        # HTML BODY
        # ==========================================

        html_body = (

            custom_body

            if custom_body

            else generate_html_body(
                employee
            )
        )

        # ==========================================
        # ACCESS TOKEN
        # ==========================================

        access_token = (
            get_access_token()
        )

        headers = {

            "Authorization":

                f"Bearer {access_token}",

            "Content-Type":
                "application/json"
        }

        # ==========================================
        # ATTACHMENTS
        # ==========================================

        attachments = []

        # ==========================================
        # INLINE IMAGES
        # ==========================================

        attachments.append(

            create_inline_attachment(

                BANNER_IMAGE,

                "banner"
            )
        )

        attachments.append(

            create_inline_attachment(

                GIFT_IMAGE,

                "gift"
            )
        )

        attachments.append(

            create_inline_attachment(

                LOGO_IMAGE,

                "logo"
            )
        )

        # ==========================================
        # CERTIFICATE ATTACHMENT
        # ==========================================

        certificate_path = employee.get(
            "certificate_path"
        )

        if (

            certificate_path

            and

            os.path.exists(
                certificate_path
            )
        ):

            with open(

                certificate_path,

                "rb"

            ) as file:

                encoded_file = base64.b64encode(

                    file.read()

                ).decode("utf-8")

            attachments.append({

                "@odata.type":

                    "#microsoft.graph.fileAttachment",

                "name":
                    Path(certificate_path).name,

                "contentBytes":
                    encoded_file
            })

        # ==========================================
        # MAIL PAYLOAD
        # ==========================================

        payload = {

            "message": {

                "subject":
                    subject,

                "body": {

                    "contentType":
                        "HTML",

                    "content":
                        html_body
                },

                "toRecipients": [

                    {
                        "emailAddress": {

                            "address":
                                recipient
                        }
                    }
                ],

                "attachments":
                    attachments
            },

            "saveToSentItems":
                True
        }

        print(
            "\n========== MAIL PAYLOAD ==========\n"
        )

        print(payload)

        print(
            "\n==================================\n"
        )

        # ==========================================
        # SEND MAIL API
        # ==========================================

        response = requests.post(

            "https://graph.microsoft.com/v1.0/me/sendMail",

            headers=headers,

            json=payload
        )

        print(
            "\n========== OUTLOOK RESPONSE ==========\n"
        )

        print(response.status_code)

        print(response.text)

        print(
            "\n======================================\n"
        )

        # ==========================================
        # FAILURE
        # ==========================================

        if response.status_code != 202:

            return {

                "success": False,

                "message":
                    response.text
            }

        # ==========================================
        # UPDATE DATABASE
        # ==========================================

        supabase.table(
            "mail_data"
        ).update({

            "mail_sent":
                True,

            "mail_sent_at":
                str(datetime.now()),

            "mail_status":
                "MAIL_SENT",

            "mail_subject":
                subject,

            "mail_body":
                html_body

        }).eq(

            "id",

            employee["id"]

        ).execute()

        print(
            "\n========== MAIL SENT SUCCESS ==========\n"
        )

        return {

            "success": True,

            "message":
                f"Mail sent to {recipient}"
        }

    except Exception as e:

        print(
            "\n========== SEND MAIL ERROR ==========\n"
        )

        print(str(e))

        print(
            "\n=====================================\n"
        )

        return {

            "success": False,

            "message":
                str(e)
        }