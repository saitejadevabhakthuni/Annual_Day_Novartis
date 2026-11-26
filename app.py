import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Event Check-In",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CSV_FILE = Path("employees.csv")


# ---------------------------------------------------------
# CUSTOM MOBILE-FRIENDLY CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        /* Hide Streamlit chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main page */
        .stApp {
            background-color: #f5f7fb;
        }

        .block-container {
            max-width: 520px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        /* Header */
        .checkin-title {
            text-align: center;
            color: #172033;
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .checkin-subtitle {
            text-align: center;
            color: #667085;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        /* Input */
        div[data-testid="stTextInput"] input {
            font-size: 18px;
            text-align: center;
            padding: 14px;
            border-radius: 10px;
        }

        /* Button */
        div[data-testid="stButton"] button {
            height: 52px;
            border-radius: 10px;
            font-size: 17px;
            font-weight: 700;
        }

        /* Result cards */
        .accepted-card {
            margin-top: 25px;
            padding: 28px 20px;
            border-radius: 16px;
            background-color: #ecfdf3;
            border: 2px solid #12b76a;
            text-align: center;
        }

        .accepted-icon {
            font-size: 48px;
        }

        .accepted-title {
            color: #067647;
            font-size: 32px;
            font-weight: 800;
            margin-top: 5px;
        }

        .accepted-text {
            color: #067647;
            font-size: 15px;
            margin-top: 6px;
        }

        .rejected-card {
            margin-top: 25px;
            padding: 28px 20px;
            border-radius: 16px;
            background-color: #fef3f2;
            border: 2px solid #f04438;
            text-align: center;
        }

        .rejected-icon {
            font-size: 48px;
        }

        .rejected-title {
            color: #b42318;
            font-size: 32px;
            font-weight: 800;
            margin-top: 5px;
        }

        .rejected-text {
            color: #b42318;
            font-size: 15px;
            margin-top: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# LOAD AND VALIDATE DATA
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"{CSV_FILE.name} was not found."
        )

    df = pd.read_csv(
        CSV_FILE,
        dtype=str,
        keep_default_na=False
    )

    # Clean column names
    df.columns = df.columns.str.strip()

    required_columns = {"521_ID", "Registered", "Type"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(sorted(missing_columns))
        )

    # Normalize data
    df["521_ID"] = (
        df["521_ID"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Registered"] = (
        df["Registered"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Type"] = (
        df["Type"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Remove rows without an ID
    df = df[df["521_ID"] != ""]

    # Avoid duplicate IDs producing unpredictable results
    df = df.drop_duplicates(
        subset=["521_ID"],
        keep="first"
    )

    return df


# ---------------------------------------------------------
# RESULT FUNCTIONS
# ---------------------------------------------------------
def show_accepted():
    st.markdown(
        """
        <div class="accepted-card">
            <div class="accepted-icon">✓</div>
            <div class="accepted-title">ACCEPTED</div>
            <div class="accepted-text">
                Registration successfully verified.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_rejected():
    st.markdown(
        """
        <div class="rejected-card">
            <div class="rejected-icon">✕</div>
            <div class="rejected-title">REJECTED</div>
            <div class="rejected-text">
                Registration could not be verified.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "Employee database is currently unavailable. "
        "Please contact the event administrator."
    )
    st.stop()

except ValueError as error:
    st.error(f"Database configuration error: {error}")
    st.stop()

except Exception:
    st.error(
        "Unable to load the employee database. "
        "Please try again later."
    )
    st.stop()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="checkin-title">
        EVENT CHECK-IN
    </div>

    <div class="checkin-subtitle">
        Enter your 521 ID to verify your registration
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# FORM
# ---------------------------------------------------------
with st.form(
    "verification_form",
    clear_on_submit=False
):

    employee_id = st.text_input(
        "521 ID",
        placeholder="Example: DEVABSA7",
        max_chars=50
    )

    submitted = st.form_submit_button(
        "VERIFY",
        use_container_width=True
    )


# ---------------------------------------------------------
# VERIFICATION
# ---------------------------------------------------------
if submitted:

    entered_id = employee_id.strip().upper()

    if not entered_id:
        st.warning("Please enter your 521 ID.")

    else:
        match = df.loc[
            df["521_ID"] == entered_id
        ]

        if match.empty:
            show_rejected()

        else:
            employee = match.iloc[0]

            registered = employee["Registered"]
            employee_type = employee["Type"]

            is_eligible = (
                registered == "YES"
                and employee_type == "INTERNAL"
            )

            if is_eligible:
                show_accepted()
            else:
                show_rejected()
