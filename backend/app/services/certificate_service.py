import os

from io import BytesIO

from pathlib import Path

from datetime import datetime

from reportlab.pdfgen import canvas

from reportlab.lib.colors import HexColor

from PyPDF2 import PdfReader, PdfWriter

from app.db.database import supabase


# ==========================================
# BASE DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


# ==========================================
# TEMPLATE PDF
# ==========================================

TEMPLATE_PDF = (

    BASE_DIR

    / "backend"

    / "certificate_templates"

    / "sample_certificate.pdf"
)

print("\n========== TEMPLATE DEBUG ==========")

print("TEMPLATE PATH:")

print(TEMPLATE_PDF)

print(
    "TEMPLATE EXISTS:",
    TEMPLATE_PDF.exists()
)

print("====================================\n")


# ==========================================
# OUTPUT FOLDER
# ==========================================

OUTPUT_FOLDER = (

    BASE_DIR

    / "backend"

    / "generated_certificates"
)

OUTPUT_FOLDER.mkdir(

    parents=True,

    exist_ok=True
)


# ==========================================
# FETCH READY TO SEND
# ==========================================

def fetch_ready_to_send_employees():

    response = (

        supabase
        .table("mail_data")

        .select("*")

        .eq(
            "status",
            "READY_TO_SEND"
        )

        .eq(
            "certificate_generated",
            False
        )

        .execute()
    )

    return response.data


# ==========================================
# FORMAT MONTH YEAR
# ==========================================

def get_month_year(date_value):

    dt = datetime.fromisoformat(
        str(date_value)
    )

    return dt.strftime(
        "%B %Y"
    )


# ==========================================
# UPDATE DB
# ==========================================

def update_certificate_details(

    employee_id,

    pdf_path

):

    update_payload = {

        "certificate_generated":
            True,

        "certificate_generated_at":
            str(datetime.now()),

        "certificate_path":
            str(pdf_path)
    }

    return (

        supabase
        .table("mail_data")

        .update(update_payload)

        .eq(
            "id",
            employee_id
        )

        .execute()
    )


# ==========================================
# CREATE CERTIFICATE
# ==========================================

def create_certificate_pdf(

    employee_name,

    award_type,

    month_year,

    output_pdf

):

    # ==========================================
    # CLEAN AWARD
    # ==========================================

    clean_award = (

        award_type

        .replace(" Award", "")

        .strip()
    )

    # ==========================================
    # READ TEMPLATE
    # ==========================================

    existing_pdf = PdfReader(
        str(TEMPLATE_PDF)
    )

    first_page = existing_pdf.pages[0]

    page_width = float(
        first_page.mediabox.width
    )

    page_height = float(
        first_page.mediabox.height
    )

    # ==========================================
    # CREATE OVERLAY
    # ==========================================

    packet = BytesIO()

    can = canvas.Canvas(

        packet,

        pagesize=(
            page_width,
            page_height
        )
    )

    # ==========================================
    # EMPLOYEE NAME
    # ==========================================

    can.setFillColor(
        HexColor("#1E3A8A")
    )

    can.setFont(
        "Times-Bold",
        34
    )

    can.drawCentredString(

        640,

        370,

        employee_name
    )

    # ==========================================
    # AWARD NAME
    # ==========================================

    can.setFillColor(
        HexColor("#F97316")
    )

    can.setFont(
        "Times-Bold",
        26
    )

    can.drawCentredString(

        640,

        286,

        clean_award
    )

    # ==========================================
    # MONTH YEAR
    # ==========================================

    can.setFillColor(
        HexColor("#1E3A8A")
    )

    can.setFont(
        "Times-Bold",
        20
    )

    can.drawCentredString(

        545,

        106,

        month_year
    )

    # ==========================================
    # SAVE OVERLAY
    # ==========================================

    can.save()

    packet.seek(0)

    # ==========================================
    # READ OVERLAY
    # ==========================================

    overlay_pdf = PdfReader(
        packet
    )

    # ==========================================
    # MERGE PDF
    # ==========================================

    output = PdfWriter()

    page = existing_pdf.pages[0]

    page.merge_page(
        overlay_pdf.pages[0]
    )

    output.add_page(page)

    # ==========================================
    # SAVE FINAL PDF
    # ==========================================

    with open(

        output_pdf,

        "wb"

    ) as output_file:

        output.write(
            output_file
        )


# ==========================================
# GENERATE SINGLE CERTIFICATE
# ==========================================

def generate_single_certificate(employee):

    employee_name = employee[
        "employee_name"
    ]

    award_type = employee[
        "award_category"
    ]

    month_year = get_month_year(
        employee["date_of_email"]
    )

    safe_name = (

        employee_name
        .replace(" ", "_")
    )

    safe_award = (

        award_type
        .replace(" ", "_")
    )

    filename = (
        f"{safe_name}_{safe_award}"
    )

    pdf_output = (

        OUTPUT_FOLDER

        / f"{filename}.pdf"
    )

    print("\n========== GENERATING ==========")

    print(employee_name)

    print(award_type)

    print(month_year)

    print("================================\n")

    # ==========================================
    # CREATE PDF
    # ==========================================

    create_certificate_pdf(

        employee_name,

        award_type,

        month_year,

        str(pdf_output)
    )

    # ==========================================
    # UPDATE DB
    # ==========================================

    update_certificate_details(

        employee["id"],

        pdf_output
    )

    print(
        "\n========== CERTIFICATE GENERATED ==========\n"
    )

    print(pdf_output)

    print(
        "\n===========================================\n"
    )

    return {

        "employee_name":
            employee_name,

        "certificate":
            str(pdf_output)
    }


# ==========================================
# GENERATE ALL CERTIFICATES
# ==========================================

def generate_all_certificates():

    employees = fetch_ready_to_send_employees()

    if len(employees) == 0:

        return {

            "success": False,

            "message":
                "No READY_TO_SEND employees found",

            "generated_count": 0
        }

    generated = []

    failed = []

    for employee in employees:

        try:

            result = generate_single_certificate(
                employee
            )

            generated.append(
                result
            )

        except Exception as e:

            print(
                "\n========== CERTIFICATE ERROR ==========\n"
            )

            print(str(e))

            print(
                "\n=======================================\n"
            )

            failed.append({

                "employee_name":
                    employee["employee_name"],

                "error":
                    str(e)
            })

    return {

        "success": True,

        "generated_count":
            len(generated),

        "failed_count":
            len(failed),

        "generated":
            generated,

        "failed":
            failed
    }