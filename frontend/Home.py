import streamlit as st

import requests

from components.sidebar import render_sidebar


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(

    page_title="Awards Dashboard",

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
    "🏠 Awards & Recognition Dashboard"
)

st.write(
    "Enterprise Mail Automation System"
)


# ==========================================
# READ MAIL BUTTON
# ==========================================

if st.button(
    "📨 Read New Mails"
):

    with st.spinner(
        "Reading mails..."
    ):

        response = requests.post(

            f"{BACKEND_URL}/trigger-mail-read"
        )

        data = response.json()

        if data["success"]:

            st.success(
                data["message"]
            )

        else:

            st.error(
                data["error"]
            )


# ==========================================
# FETCH STATS
# ==========================================

stats_response = requests.get(
    f"{BACKEND_URL}/dashboard-stats"
)

print(
    "STATUS:",
    stats_response.status_code
)

print(
    "RESPONSE:",
    stats_response.text
)

if stats_response.status_code == 200:

    stats = stats_response.json()

else:

    st.error(
        "Dashboard API failed"
    )

    st.stop()

# ==========================================
# LAST SYNC
# ==========================================

st.subheader(
    "Last Mail Sync"
)

st.info(
    str(
        stats.get("last_sync")
    )
)


# ==========================================
# STATS CARDS
# ==========================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(

        "Total Records",

        stats.get(
            "total_records"
        )
    )

with col2:

    st.metric(

        "Pending Approval",

        stats.get(
            "pending_approval"
        )
    )

with col3:

    st.metric(

        "Approved",

        stats.get(
            "approved"
        )
    )

with col4:

    st.metric(

        "Certificates",

        stats.get(
            "certificates_generated"
        )
    )

with col5:

    st.metric(

        "Mail Sent",

        stats.get(
            "mail_sent"
        )
    )
