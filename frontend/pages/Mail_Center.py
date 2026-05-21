import streamlit as st

import requests

from components.sidebar import render_sidebar


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(

    page_title="Mail Center",

    layout="wide"
)


# ==========================================
# SIDEBAR
# ==========================================

render_sidebar()


# ==========================================
# BACKEND URL
# ==========================================

BACKEND_URL = "http://127.0.0.1:8000"


# ==========================================
# TITLE
# ==========================================

st.title(
    "📨 Mail Center"
)

st.write(
    "Generate certificates and send award mails."
)


# ==========================================
# GENERATE CERTIFICATES
# ==========================================

st.subheader(
    "Generate Certificates"
)

if st.button(
    "Generate Certificates"
):

    with st.spinner(
        "Generating certificates..."
    ):

        response = requests.post(

            f"{BACKEND_URL}/generate-certificates"
        )

        data = response.json()

        if data["success"]:

            st.success(

                f"Generated "
                f"{data['generated_count']} "
                f"certificates"
            )

        else:

            st.error(
                "Certificate generation failed"
            )


st.divider()


# ==========================================
# FETCH MAIL READY EMPLOYEES
# ==========================================

response = requests.get(

    f"{BACKEND_URL}/mail-ready"
)

employees = response.json()


# ==========================================
# NO RECORDS
# ==========================================

if len(employees) == 0:

    st.info(
        "No pending mails to send."
    )

    st.stop()


# ==========================================
# SESSION STATE
# ==========================================

if "selected_employee" not in st.session_state:

    st.session_state.selected_employee = None


# ==========================================
# LAYOUT
# ==========================================

left_col, right_col = st.columns(
    [1, 2]
)


# ==========================================
# LEFT PANEL
# ==========================================

with left_col:

    st.subheader(
        "Employees"
    )

    for employee in employees:

        employee_name = employee[
            "employee_name"
        ]

        award = employee[
            "award_category"
        ]

        if st.button(

            f"{employee_name} - {award}",

            use_container_width=True,

            key=f"emp_{employee['id']}"
        ):

            st.session_state.selected_employee = employee


# ==========================================
# RIGHT PANEL
# ==========================================

with right_col:

    employee = st.session_state.selected_employee

    if employee is None:

        st.info(
            "Select employee to preview draft mail."
        )

    else:

        st.subheader(
            "Draft Mail Preview"
        )

        employee_name = employee[
            "employee_name"
        ]

        award = employee[
            "award_category"
        ]

        subject = (

            f"Congratulations "
            f"{employee_name} "
            f"on Receiving "
            f"{award}"
        )

        body = f"""
        Dear {employee_name},

        Congratulations!

        On behalf of the entire team of Ganit,
        we would like to express our admiration.

        The work you have done signifies
        new capabilities for Ganit —
        the endless dedication you have shown
        in your work, and the professionalism
        you have exhibited have not gone unnoticed;
        you are an inspiration to every fellow Ganitan.

        Please find attached your
        award certificate.

        Regards,
        HR Team
        Ganit
        """

        edited_subject = st.text_input(

            "Mail Subject",

            value=subject
        )

        edited_body = st.text_area(

            "Mail Body",

            value=body,

            height=300
        )

        # ==========================================
        # VOUCHER DETAILS
        # ==========================================

        st.subheader(
            "Voucher Details"
        )

        st.table({

            "Field": [

                "Gift Card Code",

                "Reference ID",

                "Validity",

                "Amount"
            ],

            "Value": [

                employee.get(
                    "gift_card_code",
                    "-"
                ),

                employee.get(
                    "reference_id",
                    "-"
                ),

                employee.get(
                    "validity",
                    "-"
                ),

                employee.get(
                    "amount",
                    "-"
                )
            ]
        })

        # ==========================================
        # CERTIFICATE
        # ==========================================

        st.subheader(
            "Certificate"
        )

        certificate_path = employee.get(
            "certificate_path"
        )

        if certificate_path:

            with open(

                certificate_path,

                "rb"

            ) as pdf_file:

                st.download_button(

                    "Download Certificate",

                    pdf_file,

                    file_name=certificate_path.split("\\")[-1],

                    mime="application/pdf"
                )

        # ==========================================
        # SEND BUTTON
        # ==========================================

        if st.button(

            "Send Mail",

            use_container_width=True
        ):

            with st.spinner(
                "Sending mail..."
            ):

                response = requests.post(

                    f"{BACKEND_URL}/send-mail/{employee['id']}"
                )

                data = response.json()

                if data["success"]:

                    st.success(
                        data["message"]
                    )

                    st.rerun()

                else:

                    st.error(
                        "Mail sending failed"
                    )