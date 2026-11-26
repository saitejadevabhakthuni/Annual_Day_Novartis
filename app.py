import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Event Check-In",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CSV_FILE = Path("employees.csv")

# IMPORTANT:
# After deploying your Streamlit app,
# replace this URL with your actual application URL.
APP_URL = "https://novartis-anuual-day.streamlit.app/"


# ============================================================
# PAGE STYLE
# ============================================================

st.markdown(
    """
<style>

/* Hide Streamlit default elements */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* Page */

.stApp {
    background-color: #f5f7fb;
}

.block-container {
    max-width: 600px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* Main heading */

.main-title {
    text-align: center;
    font-size: 36px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: #667085;
    font-size: 16px;
    margin-bottom: 20px;
}


/* QR */

.qr-title {
    text-align: center;
    font-size: 20px;
    font-weight: 800;
    color: #344054;
    margin-top: 10px;
}

.qr-description {
    text-align: center;
    color: #667085;
    font-size: 15px;
    margin-top: 5px;
    margin-bottom: 20px;
}


/* OR */

.or-text {
    text-align: center;
    font-size: 16px;
    font-weight: 700;
    color: #98a2b3;
    margin-top: 10px;
    margin-bottom: 15px;
}


/* Text input */

div[data-testid="stTextInput"] input {

    font-size: 20px;
    text-align: center;

    padding: 15px;

    border-radius: 10px;
}


/* Verify button */

div[data-testid="stFormSubmitButton"] button {

    height: 55px;

    border-radius: 10px;

    font-size: 18px;

    font-weight: 700;

    width: 100%;
}


/* ============================================================
   ACCEPTED
   ============================================================ */

.accepted-card {

    margin-top: 25px;

    padding: 30px 20px;

    border-radius: 18px;

    background-color: #ecfdf3;

    border: 3px solid #12b76a;

    text-align: center;
}


.accepted-icon {

    color: #12b76a;

    font-size: 55px;

    font-weight: 800;

    line-height: 1;
}


.accepted-title {

    color: #067647;

    font-size: 34px;

    font-weight: 800;

    margin-top: 12px;
}


.accepted-text {

    color: #067647;

    font-size: 16px;

    margin-top: 8px;
}


/* ============================================================
   REJECTED
   ============================================================ */

.rejected-card {

    margin-top: 25px;

    padding: 30px 20px;

    border-radius: 18px;

    background-color: #fef3f2;

    border: 3px solid #f04438;

    text-align: center;
}


.rejected-icon {

    color: #f04438;

    font-size: 55px;

    font-weight: 800;

    line-height: 1;
}


.rejected-title {

    color: #b42318;

    font-size: 34px;

    font-weight: 800;

    margin-top: 12px;
}


.rejected-text {

    color: #b42318;

    font-size: 16px;

    margin-top: 8px;
}


/* Footer */

.footer-text {

    text-align: center;

    color: #98a2b3;

    font-size: 12px;

    margin-top: 40px;
}


/* Mobile */

@media (max-width: 600px) {

    .block-container {
        padding-left: 20px;
        padding-right: 20px;
    }

    .main-title {
        font-size: 30px;
    }

    .accepted-title,
    .rejected-title {
        font-size: 30px;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD CSV
# ============================================================

@st.cache_data(ttl=60)
def load_data():

    if not CSV_FILE.exists():
        raise FileNotFoundError("employees.csv not found")

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
            "Missing column(s): "
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

    # Remove empty IDs

    df = df[
        df["521_ID"] != ""
    ]

    # Remove duplicates

    df = df.drop_duplicates(
        subset=["521_ID"],
        keep="first"
    )

    return df


# ============================================================
# GENERATE QR
# ============================================================

@st.cache_data
def generate_qr(url):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(url)

    qr.make(
        fit=True
    )

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


# ============================================================
# ACCEPTED RESULT
# IMPORTANT:
# HTML is intentionally NOT indented.
# ============================================================

def show_accepted():

    st.markdown(
        """<div class="accepted-card">
<div class="accepted-icon">✓</div>
<div class="accepted-title">ACCEPTED</div>
<div class="accepted-text">Your registration has been successfully verified.</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# REJECTED RESULT
# ============================================================

def show_rejected():

    st.markdown(
        """<div class="rejected-card">
<div class="rejected-icon">✕</div>
<div class="rejected-title">REJECTED</div>
<div class="rejected-text">Your registration could not be verified.</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# LOAD EMPLOYEE DATABASE
# ============================================================

try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "Employee database is currently unavailable."
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


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """<div class="main-title">EVENT CHECK-IN</div>
<div class="subtitle">Scan the QR code or enter your 521 ID</div>""",
    unsafe_allow_html=True
)


# ============================================================
# QR CODE
# ============================================================

qr_image = generate_qr(
    APP_URL
)

left, center, right = st.columns(
    [1.2, 1.6, 1.2]
)

with center:

    st.image(
        qr_image,
        use_container_width=True
    )


st.markdown(
    """<div class="qr-title">SCAN TO CHECK IN</div>
<div class="qr-description">Scan using your phone camera to open the check-in page</div>""",
    unsafe_allow_html=True
)


# ============================================================
# OR
# ============================================================

st.markdown(
    """<div class="or-text">──────── OR ────────</div>""",
    unsafe_allow_html=True
)


# ============================================================
# FORM
# ============================================================

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


# ============================================================
# VERIFICATION
# ============================================================

if submitted:

    # Clean employee input
    entered_id = employee_id.strip().upper()

    # --------------------------------------------
    # EMPTY
    # --------------------------------------------

    if not entered_id:

        st.warning(
            "Please enter your 521 ID."
        )

    else:

        # ----------------------------------------
        # FIND 521 ID
        # ----------------------------------------

        match = df.loc[
            df["521_ID"] == entered_id
        ]

        # ----------------------------------------
        # ID NOT FOUND
        # ----------------------------------------

        if match.empty:

            show_rejected()

        else:

            # ------------------------------------
            # GET EMPLOYEE RECORD
            # ------------------------------------

            employee = match.iloc[0]

            registered = employee["Registered"]

            employee_type = employee["Type"]


            # ------------------------------------
            # ELIGIBILITY RULE
            #
            # ID must exist
            # Registered = YES
            # Type = INTERNAL
            # ------------------------------------

            is_eligible = (
                registered == "YES"
                and
                employee_type == "INTERNAL"
            )


            # ------------------------------------
            # SHOW RESULT
            # ------------------------------------

            if is_eligible:

                show_accepted()

            else:

                show_rejected()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """<div class="footer-text">Event Registration Verification</div>""",
    unsafe_allow_html=True
)
