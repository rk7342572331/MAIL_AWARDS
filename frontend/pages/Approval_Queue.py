import streamlit as st
import requests
import pandas as pd


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(

    page_title="HR Approval Queue",

    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title(
    "HR Approval Dashboard"
)

BACKEND_URL = (
    "https://mail-awards-backend.onrender.com"
)


# ==========================================
# FETCH PENDING APPROVALS
# ==========================================

response = requests.get(
    f"{BACKEND_URL}/pending-approvals"
)

response_json = response.json()

data = response_json.get(
    "data",
    []
)


# ==========================================
# NO DATA
# ==========================================

if len(data) == 0:

    st.success(
        "No Pending Approvals"
    )


# ==========================================
# EMPLOYEE CARDS
# ==========================================

for employee in data:

    with st.container():

        st.markdown("---")

        col1, col2 = st.columns([4, 1])

        # ==========================================
        # LEFT SIDE
        # ==========================================

        with col1:

            st.subheader(
                employee.get(
                    "employee_name",
                    "N/A"
                )
            )

            st.write(
                f"🏆 Award Category: "
                f"{employee.get('award_category', 'N/A')}"
            )

            st.write(
                f"📅 Quarter: "
                f"{employee.get('quarter', 'N/A')}"
            )

            st.write(
                f"👤 Nominated By: "
                f"{employee.get('nominated_by', 'N/A')}"
            )

            st.write(
                f"💼 Project: "
                f"{employee.get('project', 'N/A')}"
            )

            st.write(
                "⭐ Achievement Reason:"
            )

            st.info(
                employee.get(
                    "achievement_reason",
                    "N/A"
                )
            )

        # ==========================================
        # RIGHT SIDE
        # ==========================================

        with col2:

            # ==========================================
            # APPROVE BUTTON
            # ==========================================

            if st.button(

                "✅ Approve",

                key=f"approve_{employee['id']}"

            ):

                requests.post(

                    f"{BACKEND_URL}/approve/"
                    f"{employee['id']}"

                )

                st.success(
                    "Approved Successfully"
                )

                st.rerun()

            st.write("")
            st.write("")

            # ==========================================
            # REJECTION REASON
            # ==========================================

            rejection_reason = st.text_area(

                "Reason For Rejection",

                key=f"reject_reason_{employee['id']}"

            )

            # ==========================================
            # REJECT BUTTON
            # ==========================================

            if st.button(

                "❌ Reject",

                key=f"reject_{employee['id']}"

            ):

                if rejection_reason.strip() == "":

                    st.error(
                        "Please enter rejection reason"
                    )

                else:

                    requests.post(

                        f"{BACKEND_URL}/reject",

                        json={

                            "record_id":
                                employee["id"],

                            "rejection_reason":
                                rejection_reason
                        }

                    )

                    st.success(
                        "Rejected Successfully"
                    )

                    st.rerun()


# ==========================================
# VOUCHER ALLOCATION SECTION
# ==========================================

st.markdown("---")

st.header(
    "Voucher Allocation"
)

st.write(
    """
This will allocate vouchers to all
APPROVED_PENDING_REWARD employees.
"""
)
# ==========================================
# ALLOCATE BUTTON
# ==========================================

if st.button(
    "🎁 Allocate Vouchers"
):

    try:

        allocation_response = requests.post(

            f"{BACKEND_URL}/allocate-vouchers"

        )

        allocation_data = (
            allocation_response.json()
        )

        # ==========================================
        # SUCCESS
        # ==========================================

        if allocation_data.get("success"):

            st.success(

                f"✅ Successfully Allocated To "
                f"{allocation_data.get('allocated_count', 0)} "
                f"Employees"

            )

        # ==========================================
        # FAILURE
        # ==========================================

        else:

            st.error(

                allocation_data.get(
                    "message",
                    "Allocation Failed"
                )

            )

    # ==========================================
    # EXCEPTION
    # ==========================================

    except Exception as e:

        st.error(
            f"ERROR: {str(e)}"
        )
