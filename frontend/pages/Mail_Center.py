import os

import streamlit as st

import pandas as pd

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

BACKEND_URL = (
    "https://mail-awards-backend.onrender.com"
)


# ==========================================
# TITLE
# ==========================================

st.title(
    "📧 Mail Center"
)

st.write(
    "Manage and send employee award mails."
)


# ==========================================
# FETCH MAIL READY RECORDS
# ==========================================

try:

    response = requests.get(

        f"{BACKEND_URL}/mail-ready"
    )

    employees = response.json()

except Exception as e:

    st.error(str(e))

    st.stop()


# ==========================================
# EMPTY
# ==========================================

if len(employees) == 0:

    st.info(
        "No mail-ready employees found."
    )

    st.stop()


# ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(
    employees
)


# ==========================================
# DISPLAY RECORDS
# ==========================================

for _, employee in df.iterrows():

    with st.container():

        st.markdown("---")

        # ==========================================
        # BASIC INFO
        # ==========================================

        col1, col2 = st.columns([2, 1])

        with col1:

            st.subheader(
                employee["employee_name"]
            )

            st.write(
                f"🏆 Award: {employee['award_category']}"
            )

            st.write(
                f"📧 Mail: {employee['employee_mailid']}"
            )

            st.write(
                f"🆔 Employee ID: {employee['employee_id']}"
            )

            st.write(
                f"🏢 Department: {employee['department']}"
            )

            st.write(
                f"🎁 Voucher: {employee.get('gift_card_code', '-')}"
            )

            st.write(
                f"💰 Amount: ₹ {employee.get('amount', '-')}"
            )

        with col2:

            st.success(
                employee["status"]
            )

        # ==========================================
        # CERTIFICATE DOWNLOAD
        # ==========================================

        certificate_path = employee.get(
            "certificate_path"
        )

        st.subheader(
            "Certificate"
        )

        if (

            certificate_path

            and

            os.path.exists(
                certificate_path
            )

        ):

            try:

                with open(

                    certificate_path,

                    "rb"

                ) as pdf_file:

                    st.download_button(

                        label="📄 Download Certificate",

                        data=pdf_file,

                        file_name=f"{employee['employee_name']}_certificate.pdf",

                        mime="application/pdf",

                        key=f"download_{employee['id']}"
                    )

            except Exception as e:

                st.warning(
                    f"Certificate open error: {str(e)}"
                )

        else:

            st.warning(
                "Certificate file not found on cloud server."
            )

        # ==========================================
        # MAIL PREVIEW
        # ==========================================

        st.subheader(
            "Mail Preview"
        )

        default_subject = (

            employee.get(
                "mail_subject"
            )

            or

            f"Congratulations "
            f"{employee['employee_name']} "
            f"on Receiving "
            f"{employee['award_category']}"
        )

        default_body = (

            employee.get(
                "mail_body"
            )

            or

            f"""
            Dear {employee['employee_name']},

            Congratulations on receiving
            {employee['award_category']}.

            Regards,
            Ganit Team
            """
        )

        subject = st.text_input(

            "Subject",

            value=default_subject,

            key=f"subject_{employee['id']}"
        )

        body = st.text_area(

            "Body",

            value=default_body,

            height=250,

            key=f"body_{employee['id']}"
        )

        # ==========================================
        # SEND BUTTON
        # ==========================================

        if st.button(

            f"Send Mail to {employee['employee_name']}",

            key=f"send_{employee['id']}"
        ):

            payload = {

                "custom_subject":
                    subject,

                "custom_body":
                    body
            }

            try:

                send_response = requests.post(

                    f"{BACKEND_URL}/send-mail/{employee['id']}",

                    json=payload
                )

                result = send_response.json()

                if result.get("success"):

                    st.success(
                        result["message"]
                    )

                else:

                    st.error(
                        result.get(
                            "message",
                            "Mail sending failed"
                        )
                    )

            except Exception as e:

                st.error(str(e))