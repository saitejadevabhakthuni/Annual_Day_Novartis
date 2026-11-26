import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from pathlib import Path

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Event Check-In",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CSV_FILE = Path("employees.csv")

# IMPORTANT:
# Replace this with your actual deployed Streamlit URL
APP_URL = "https://your-event-checkin.streamlit.app"


# =========================================================
# PAGE DESIGN
# =========================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        max-width: 550px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        text-align: center;
        font-size: 34px;
        font-weight: 800;
        color: #172033;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #667085;
        font-size: 16px;
        margin-bottom: 15px;
    }

    .qr-title {
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        color: #344054;
        margin-top: 8px;
        margin-bottom: 4px;
    }

    .qr-description {
        text-align: center;
        color: #667085;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .or-text {
        text-align: center;
        font-size: 14px;
        font-weight: 700;
        color: #98a2b3;
        margin-top: 5px;
        margin-bottom: 5px;
    }

    div[data-testid="stTextInput"] input {
        font-size: 18px;
        text-align: center;
        padding: 14px;
        border-radius: 10px;
    }

    div[data-testid="stButton"] button {
        height: 52px;
        border-radius: 10px;
        font-size: 17px;
        font-weight: 700;
    }

    .accepted-card {
        margin-top: 25px;
        padding: 28px 20px;
        border-radius: 16px;
        background-color: #ecfdf3;
        border: 2px solid #12b76a;
        text-align: center;
    }

    .accepted-icon {
        color: #12b76a;
        font-size: 50px;
        font-weight: 800;
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
        margin-top: 8px;
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
        color: #f04438;
        font-size: 50px;
        font-weight: 800;
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
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD EMPLOYEE DATA
# =========================================================

@st.cache_data(ttl=60)
def load_data():

    if not CSV_FILE.exists():
        raise FileNotFoundError("employees.csv not found.")

    df = pd.read_csv(
        CSV_FILE,
        dtype=str,
        keep_default_na=False
    )

    # Clean column names
    df.columns = df.columns.str.strip()

    required_columns = {
        "521_ID",
        "Registered",
        "Type"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required column(s): "
            + ", ".join(sorted(missing_columns))
        )

    # Clean ID values
    df["521_ID"] = (
        df["521_ID"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Clean registration values
    df["Registered"] = (
        df["Registered"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Clean employee type values
    df["Type"] = (
        df["Type"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Remove rows that do not contain an ID
    df = df[df["521_ID"] != ""]

    # Remove duplicate IDs
    df = df.drop_duplicates(
        subset=["521_ID"],
        keep="first"
    )

    return df


# =========================================================
# GENERATE QR CODE
# =========================================================

@st.cache_data
def generate_qr(url):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(url)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# RESULT FUNCTIONS
# =========================================================

def show_accepted():

    st.markdown(
        """
        <div class="accepted-card">

            <div class="accepted-icon">
                ✓
            </div>

            <div class="accepted-title">
                ACCEPTED
            </div>

            <div class="accepted-text">
                Your registration has been successfully verified.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def show_rejected():

    st.markdown(
        """
        <div class="rejected-card">

            <div class="rejected-icon">
                ✕
            </div>

            <div class="rejected-title">
                REJECTED
            </div>

            <div class="rejected-text">
                Your registration could not be verified.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# LOAD DATABASE
# =========================================================

try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "Employee database is currently unavailable. "
        "Please contact the event administrator."
    )

    st.stop()

except ValueError as error:

    st.error(
        f"Database configuration error: {error}"
    )

    st.stop()

except Exception:

    st.error(
        "Unable to load the employee database. "
        "Please try again later."
    )

    st.stop()


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    """
    <div class="main-title">
        EVENT CHECK-IN
    </div>

    <div class="subtitle">
        Scan the QR code or enter your 521 ID
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# QR CODE
# =========================================================

qr_image = generate_qr(APP_URL)

col1, col2, col3 = st.columns(
    [1, 1.5, 1]
)

with col2:

    st.image(
        qr_image,
        use_container_width=True
    )


st.markdown(
    """
    <div class="qr-title">
        SCAN TO CHECK IN
    </div>

    <div class="qr-description">
        Scan using your phone camera to open the check-in page
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DIVIDER
# =========================================================

st.markdown(
    """
    <div class="or-text">
        ───────── OR ─────────
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CHECK-IN FORM
# =========================================================

with st.form(
    "verification_form",
    clear_on_submit=False
):

    employee_id = st.text_input(
        "Enter your 521 ID",
        placeholder="Example: DEVABSA7",
        max_chars=50
    )

    submitted = st.form_submit_button(
        "VERIFY",
        use_container_width=True
    )


# =========================================================
# VALIDATION
# =========================================================

if submitted:

    entered_id = employee_id.strip().upper()

    # Empty input
    if not entered_id:

        st.warning(
            "Please enter your 521 ID."
        )

    else:

        # Search employee
        match = df.loc[
            df["521_ID"] == entered_id
        ]

        # ID does not exist
        if match.empty:

            show_rejected()

        else:

            employee = match.iloc[0]

            registered = employee["Registered"]
            employee_type = employee["Type"]

            # -------------------------------------------------
            # ACCEPTANCE RULE
            # -------------------------------------------------

            is_eligible = (
                registered == "YES"
                and employee_type == "INTERNAL"
            )

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            if is_eligible:

                show_accepted()

            else:

                show_rejected()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <br><br>

    <p style="
        text-align:center;
        color:#98a2b3;
        font-size:12px;
    ">
        Event Registration Verification
    </p>
    """,
    unsafe_allow_html=True
)
