import base64
import html
from io import BytesIO
from pathlib import Path

import pandas as pd
import qrcode
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Annual Day Event Check-In",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSV_FILE = Path("employees.csv")

# IMPORTANT:
# Replace with your exact deployed Streamlit URL.
# Check the spelling ("anuual" vs "annual") - the QR must match exactly.
APP_URL = "https://novartis-anuual-day.streamlit.app/"

# Phones that open the page via QR get ?src=qr,
# so they see only the form (not the QR again).
QR_TARGET = f"{APP_URL}?src=qr"

opened_from_qr = st.query_params.get("src") == "qr"


# ============================================================
# PAGE STYLE  (Orange / Black / Silver theme)
# ============================================================

st.markdown(
    """
<style>

/* ---------- Hide Streamlit default elements ---------- */

#MainMenu,
footer,
header {
    visibility: hidden;
}

div[data-testid="InputInstructions"] {
    display: none;
}


/* ---------- Page background: black -> silver ---------- */

.stApp {
    background: linear-gradient(
        160deg,
        #000000 0%,
        #141414 35%,
        #2b2d31 65%,
        #8e9196 100%
    ) !important;
    background-attachment: fixed !important;
}

/* Orange accent bar at the top */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: linear-gradient(90deg, #ff5f00, #ff9f1c, #ffd089, #ff9f1c, #ff5f00);
    z-index: 1000;
}

.block-container {
    max-width: 520px;
    padding-top: 2.5rem;
    padding-bottom: 2rem;
}


/* ---------- Header ---------- */

.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 6px;
    background: linear-gradient(90deg, #ff6a00, #ffb347);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.subtitle {
    text-align: center;
    color: #c0c4cc;
    font-size: 16px;
    margin-bottom: 24px;
}


/* ---------- Shared silver card (QR card + form) ---------- */

.qr-card,
div[data-testid="stForm"] {
    background: linear-gradient(
        145deg,
        #f4f5f7 0%,
        #dcdfe4 50%,
        #b9bdc4 100%
    ) !important;
    border: 2px solid #ff7a00 !important;
    border-radius: 20px !important;
    box-shadow:
        0 8px 24px rgba(255, 122, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    padding: 24px !important;
}


/* ---------- QR ---------- */

.qr-card {
    text-align: center;
}

.qr-card img {
    width: 200px;
    max-width: 70%;
    height: auto;
    display: block;
    margin: 0 auto;
    padding: 10px;
    background-color: #ffffff;
    border: 3px solid #111111;
    border-radius: 14px;
}

.qr-title {
    font-size: 18px;
    font-weight: 900;
    color: #111111;
    margin-top: 14px;
    letter-spacing: 0.5px;
}

.qr-description {
    color: #3a3d42;
    font-size: 14px;
    margin-top: 4px;
}


/* ---------- OR divider ---------- */

.divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0;
}

.divider::before,
.divider::after {
    content: "";
    flex: 1;
    height: 2px;
    background: linear-gradient(90deg, transparent, #c0c0c0, transparent);
}

.divider span {
    background: linear-gradient(135deg, #ff6a00, #ffa53a);
    color: #000000;
    font-size: 13px;
    font-weight: 900;
    padding: 6px 14px;
    border-radius: 999px;
    box-shadow: 0 0 12px rgba(255, 122, 0, 0.5);
}


/* ---------- Form ---------- */

.form-label {
    text-align: center;
    font-size: 16px;
    font-weight: 800;
    color: #111111;
    margin-bottom: 8px;
}

div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border-color: #111111 !important;
    border-radius: 12px !important;
}

div[data-testid="stTextInput"] div[data-baseweb="input"] {
    border: 2px solid #111111 !important;
}

div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: #ff7a00 !important;
    box-shadow: 0 0 0 3px rgba(255, 122, 0, 0.3);
}

div[data-testid="stTextInput"] input {
    font-size: 20px;
    font-weight: 700;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 14px;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    background-color: #ffffff !important;
    caret-color: #ff7a00;
}

div[data-testid="stTextInput"] input::placeholder {
    text-transform: none;
    letter-spacing: normal;
    font-weight: 400;
    color: #8e9196 !important;
    -webkit-text-fill-color: #8e9196 !important;
}

div[data-testid="stFormSubmitButton"] button {
    height: 54px;
    width: 100%;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #ff5f00 0%, #ff9f1c 100%) !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
    margin-top: 8px;
    box-shadow: 0 6px 16px rgba(255, 106, 0, 0.4);
    transition: all 0.2s ease;
}

div[data-testid="stFormSubmitButton"] button p {
    font-size: 18px !important;
    font-weight: 900 !important;
    letter-spacing: 1px;
}

div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:focus {
    background: #000000 !important;
    color: #ff9f1c !important;
    border: 2px solid #ff7a00 !important;
    transform: translateY(-1px);
}

div[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(1px);
}


/* ---------- Result cards ---------- */

.result-card {
    margin-top: 24px;
    padding: 28px 20px;
    border-radius: 18px;
    text-align: center;
    color: #ffffff;
    border: 2px solid #c0c0c0;
    animation: fadeIn 0.25s ease-out;
}

.result-card.ok {
    background: linear-gradient(135deg, #064e2b 0%, #12b76a 100%);
    box-shadow: 0 0 24px rgba(18, 183, 106, 0.5);
}

.result-card.bad {
    background: linear-gradient(135deg, #7a1010 0%, #f04438 100%);
    box-shadow: 0 0 24px rgba(240, 68, 56, 0.5);
}

.result-icon {
    font-size: 54px;
    font-weight: 900;
    line-height: 1;
}

.result-title {
    font-size: 32px;
    font-weight: 900;
    margin-top: 10px;
    letter-spacing: 1px;
}

.result-text {
    font-size: 16px;
    margin-top: 6px;
}

.result-id {
    display: inline-block;
    font-size: 14px;
    margin-top: 12px;
    padding: 4px 12px;
    border-radius: 999px;
    background-color: rgba(0, 0, 0, 0.35);
    font-family: monospace;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: none; }
}


/* ---------- Footer ---------- */

.footer-text {
    text-align: center;
    color: #c0c4cc;
    font-size: 12px;
    margin-top: 36px;
    letter-spacing: 0.5px;
}

.footer-text span {
    color: #ff9f1c;
    font-weight: 700;
}


/* ---------- Mobile ---------- */

@media (max-width: 600px) {

    .block-container {
        padding-left: 16px;
        padding-right: 16px;
    }

    .main-title {
        font-size: 30px;
    }

    .result-title {
        font-size: 28px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOAD CSV
# ============================================================

@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:

    if not CSV_FILE.exists():
        raise FileNotFoundError("employees.csv not found")

    df = pd.read_csv(
        CSV_FILE,
        dtype=str,
        keep_default_na=False,
    )

    # Clean column names
    df.columns = df.columns.str.strip()

    required_columns = {"521_ID", "Registered", "Type"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing column(s): " + ", ".join(sorted(missing_columns))
        )

    # Normalize data
    for col in ["521_ID", "Registered", "Type"]:
        df[col] = df[col].astype(str).str.strip().str.upper()

    # Remove empty IDs and duplicates
    df = df[df["521_ID"] != ""]
    df = df.drop_duplicates(subset=["521_ID"], keep="first")

    return df


# ============================================================
# GENERATE QR (base64 for exact centering)
# ============================================================

@st.cache_data
def generate_qr_base64(url: str) -> str:

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )

    qr.add_data(url)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()


# ============================================================
# RESULT CARD (ACCEPTED / REJECTED)
# ============================================================

def show_result(accepted: bool, entered_id: str) -> None:

    if accepted:
        css_class = "ok"
        icon = "✓"
        title = "ACCEPTED"
        text = "Your registration has been successfully verified."
    else:
        css_class = "bad"
        icon = "✕"
        title = "REJECTED"
        text = "Your registration could not be verified."

    safe_id = html.escape(entered_id)

    st.markdown(
        f'<div class="result-card {css_class}" role="status" aria-live="polite">'
        f'<div class="result-icon">{icon}</div>'
        f'<div class="result-title">{title}</div>'
        f'<div class="result-text">{text}</div>'
        f'<div class="result-id">ID: {safe_id}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD EMPLOYEE DATABASE
# ============================================================

try:
    df = load_data()

except FileNotFoundError:
    st.error("Employee database is currently unavailable.")
    st.stop()

except ValueError as error:
    st.error(f"Database configuration error: {error}")
    st.stop()

except Exception:
    st.error("Unable to load the employee database. Please try again later.")
    st.stop()


# ============================================================
# PAGE HEADER
# ============================================================

subtitle = (
    "Enter your 521 ID to check in"
    if opened_from_qr
    else "Scan the QR code or enter your 521 ID"
)

st.markdown(
    f'<div class="main-title">ANNUAL DAY EVENT CHECK-IN</div>'
    f'<div class="subtitle">{subtitle}</div>',
    unsafe_allow_html=True,
)


# ============================================================
# QR CODE (kiosk / display screen only)
# ============================================================

if not opened_from_qr:

    qr_b64 = generate_qr_base64(QR_TARGET)

    st.markdown(
        f'<div class="qr-card">'
        f'<img src="data:image/png;base64,{qr_b64}" alt="Check-in QR code">'
        f'<div class="qr-title">SCAN TO CHECK IN</div>'
        f'<div class="qr-description">Use your phone camera to open the check-in page</div>'
        f'</div>'
        f'<div class="divider"><span>OR</span></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# FORM
# ============================================================

with st.form("verification_form", clear_on_submit=False):

    st.markdown(
        '<div class="form-label">Enter your 521 ID</div>',
        unsafe_allow_html=True,
    )

    employee_id = st.text_input(
        "521 ID",
        placeholder="e.g. DEVABSA7",
        max_chars=50,
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button(
        "VERIFY",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# VERIFICATION
#
# Eligibility rule:
#   - ID must exist
#   - Registered = YES
#   - Type = INTERNAL
# ============================================================

if submitted:

    entered_id = employee_id.strip().upper()

    if not entered_id:
        st.warning("Please enter your 521 ID.")

    else:
        match = df.loc[df["521_ID"] == entered_id]

        is_eligible = (
            not match.empty
            and match.iloc[0]["Registered"] == "YES"
            and match.iloc[0]["Type"] == "INTERNAL"
        )

        show_result(is_eligible, entered_id)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-text">Event Registration <span>Verification</span></div>',
    unsafe_allow_html=True,
)
