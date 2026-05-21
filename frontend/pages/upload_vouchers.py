import streamlit as st
import pandas as pd
import sys
import os


# ==========================================
# ADD BACKEND PATH
# ==========================================

sys.path.append(

    os.path.abspath(

        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )

    )

)


from backend.app.services.voucher_service import (

    process_voucher_file,

    get_all_vouchers,

    get_voucher_stats

)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(

    page_title="Upload Vouchers",

    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title(
    "Voucher Upload & Management"
)


# ==========================================
# VOUCHER STATS
# ==========================================

stats = get_voucher_stats()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Vouchers",
        stats["total"]
    )

with col2:

    st.metric(
        "Assigned",
        stats["assigned"]
    )

with col3:

    st.metric(
        "Unassigned",
        stats["unassigned"]
    )


st.markdown("---")


# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(

    "Upload Voucher Excel/CSV",

    type=["xlsx", "csv"]

)


# ==========================================
# PROCESS FILE
# ==========================================

if uploaded_file is not None:

    # ==========================================
    # READ FILE
    # ==========================================

    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(
            uploaded_file
        )

    else:

        df = pd.read_excel(
            uploaded_file
        )

    # ==========================================
    # LOWERCASE COLUMNS
    # ==========================================

    df.columns = [

        col.strip().lower()

        for col in df.columns
    ]

    st.subheader(
        "Uploaded File Preview"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # ==========================================
    # UPLOAD BUTTON
    # ==========================================

    if st.button(
        "Upload Vouchers"
    ):

        result = (
            process_voucher_file(df)
        )

        st.success(

            f"Inserted: "
            f"{result['inserted']}"

        )

        st.warning(

            f"Duplicates Skipped: "
            f"{result['duplicates']}"

        )

        st.rerun()


# ==========================================
# STORED VOUCHERS
# ==========================================

st.markdown("---")

st.subheader(
    "Stored Voucher Data"
)

voucher_data = get_all_vouchers()

if len(voucher_data) > 0:

    voucher_df = pd.DataFrame(
        voucher_data
    )

    st.dataframe(

        voucher_df,

        use_container_width=True

    )

else:

    st.info(
        "No vouchers uploaded yet"
    )