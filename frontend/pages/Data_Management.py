import streamlit as st

import pandas as pd

import requests

from io import BytesIO

from components.sidebar import render_sidebar


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(

    page_title="Data Management",

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
    "📊 Data Management"
)


# ==========================================
# TABLE SELECTOR
# ==========================================

table_name = st.selectbox(

    "Select Table",

    [

        "mail_data",

        "voucher_master",

        "employee_master",

        "mail_sync_tracker"
    ]
)


# ==========================================
# FETCH DATA
# ==========================================

response = requests.get(

    f"{BACKEND_URL}/table-data/{table_name}"
)

records = response.json()


# ==========================================
# EMPTY CHECK
# ==========================================

if len(records) == 0:

    st.info(
        "No records found."
    )

    st.stop()


# ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(
    records
)


# ==========================================
# SHOW DATA
# ==========================================

st.subheader(
    f"{table_name} Records"
)

edited_df = st.data_editor(

    df,

    use_container_width=True,

    num_rows="dynamic"
)


# ==========================================
# SAVE CHANGES
# ==========================================

if st.button(
    "Save Changes"
):

    with st.spinner(
        "Updating records..."
    ):

        for _, row in edited_df.iterrows():

            record_id = row["id"]

            payload = row.to_dict()

            requests.put(

                f"{BACKEND_URL}/update-record/"
                f"{table_name}/"
                f"{record_id}",

                json=payload
            )

        st.success(
            "Records updated successfully"
        )

        st.rerun()


# ==========================================
# DELETE RECORD
# ==========================================

st.subheader(
    "Delete Record"
)

record_id_to_delete = st.number_input(

    "Enter Record ID",

    min_value=1,

    step=1
)

if st.button(
    "Delete Selected Record"
):

    response = requests.delete(

        f"{BACKEND_URL}/delete-record/"
        f"{table_name}/"
        f"{record_id_to_delete}"
    )

    data = response.json()

    if data["success"]:

        st.success(
            data["message"]
        )

        st.rerun()

    else:

        st.error(
            "Delete failed"
        )


# ==========================================
# DOWNLOAD EXCEL
# ==========================================

st.subheader(
    "Download Excel"
)

excel_buffer = BytesIO()

with pd.ExcelWriter(

    excel_buffer,

    engine="openpyxl"
) as writer:

    edited_df.to_excel(

        writer,

        index=False,

        sheet_name=table_name
    )

excel_data = excel_buffer.getvalue()

st.download_button(

    label="Download Excel",

    data=excel_data,

    file_name=f"{table_name}.xlsx",

    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    )
)
