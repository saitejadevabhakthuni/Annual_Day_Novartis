import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Event Check-In",
    layout="centered"
)

CSV_FILE = "employees.csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_FILE, dtype=str)

    df.columns = df.columns.str.strip()

    df["521_ID"] = df["521_ID"].astype(str).str.strip().str.upper()
    df["Registered"] = df["Registered"].astype(str).str.strip().str.upper()
    df["Type"] = df["Type"].astype(str).str.strip().str.upper()

    return df

df = load_data()

st.markdown(
    """
    <h1 style="text-align:center;">EVENT CHECK-IN</h1>
    <p style="text-align:center;">Enter your 521 ID to verify check-in status</p>
    """,
    unsafe_allow_html=True
)

employee_id = st.text_input(
    "Enter 521 ID",
    placeholder="Example: DEVABSA7"
)

if st.button("VERIFY", use_container_width=True):
    entered_id = employee_id.strip().upper()

    if entered_id == "":
        st.warning("Please enter 521 ID")
    else:
        match = df[df["521_ID"] == entered_id]

        if not match.empty:
            registered = match.iloc[0]["Registered"]
            employee_type = match.iloc[0]["Type"]

            if registered == "YES" and employee_type == "INTERNAL":
                st.markdown(
                    """
                    <h1 style="text-align:center; color:green;">
                    ACCEPTED
                    </h1>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <h1 style="text-align:center; color:red;">
                    REJECTED
                    </h1>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <h1 style="text-align:center; color:red;">
                REJECTED
                </h1>
                """,
                unsafe_allow_html=True
            )
