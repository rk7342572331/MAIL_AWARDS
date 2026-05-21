import streamlit as st


def render_sidebar():

    st.sidebar.title(
        "Awards System"
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### Navigation"
    )

    st.sidebar.markdown(

        """
        <a href="http://localhost:8501/Approval_Queue" target="_self">
            <button style="
                width:100%;
                padding:10px;
                margin-bottom:10px;
                border-radius:10px;
                border:none;
                background-color:#4CAF50;
                color:white;
                font-size:16px;
                cursor:pointer;
            ">
                HR Approval Queue
            </button>
        </a>
        """,

        unsafe_allow_html=True
    )

    st.sidebar.markdown(

        """
        <a href="http://localhost:8501/Upload_Vouchers" target="_self">
            <button style="
                width:100%;
                padding:10px;
                border-radius:10px;
                border:none;
                background-color:#2196F3;
                color:white;
                font-size:16px;
                cursor:pointer;
            ">
                Upload Vouchers
            </button>
        </a>
        """,

        unsafe_allow_html=True
    )
    
    st.sidebar.page_link(

    "pages/Mail_Center.py",

    label="📨 Mail Center"
)
    
    st.sidebar.page_link(

    "pages/Data_Management.py",

    label="📊 Data Management"
)