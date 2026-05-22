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

BACKEND_URL = "https://mail-awards-backend.onrender.com"


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

            st.rerun()

        else:

            st.error(

                data.get(
                    "message",
                    "Certificate generation failed"
                )
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

        button_label = (

            f"{employee_name}"
            f" - "
            f"{award}"
        )

        if st.button(

            button_label,

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

            employee.get(
                "mail_subject"
            )

            or

            f"Congratulations "
            f"{employee_name} "
            f"on Receiving "
            f"{award}"
        )

        body = (

            employee.get(
                "mail_body"
            )

            or

            f"""
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
        )

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

        certificate_url = employee.get(
            "certificate_path"
        )

        if certificate_url:

            st.link_button(

                "📄 Open Certificate",

                certificate_url
            )

        else:

            st.warning(
                "Certificate not available"
            )

        # ==========================================
        # SEND MAIL
        # ==========================================

        st.subheader(
            "Send Mail"
        )

        if st.button(

            "Send Mail",

            use_container_width=True
        ):

            with st.spinner(
                "Sending mail..."
            ):

                payload = {

                    "custom_subject":
                        edited_subject,

                    "custom_body":
                        edited_body
                }

                response = requests.post(

                    f"{BACKEND_URL}/send-mail/{employee['id']}",

                    json=payload
                )

                data = response.json()

                if data["success"]:

                    st.success(
                        data["message"]
                    )

                    st.rerun()

                else:

                    st.error(

                        data.get(
                            "message",
                            "Mail sending failed"
                        )
                    )