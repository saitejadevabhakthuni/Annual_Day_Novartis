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
    page_title="Event Check-In",
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
# PAGE STYLE
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

/* Hide "Press Enter to submit form" hint */
div[data-testid="InputInstructions"] {
    display: none;
}


/* ---------- Page ---------- */

.stApp {
    background-color: #f5f7fb;
}

.block-container {
    max-width: 520px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}


/* ---------- Header ---------- */

.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
    color: #172033;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.subtitle {
    text-align: center;
    color: #667085;
    font-size: 16px;
    margin-bottom: 24px;
}


/* ---------- Shared card look (QR card + form) ---------- */

.qr-card,
div[data-testid="stForm"] {
    background-color: #ffffff;
    border: 1px solid #e4e7ec !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 16px rgba(16, 24, 40, 0.06);
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
}

.qr-title {
    font-size: 18px;
    font-weight: 800;
    color: #344054;
    margin-top: 12px;
}

.qr-description {
    color: #667085;
    font-size: 14px;
    margin-top: 4px;
}


/* ---------- OR divider ---------- */

.divider {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #98a2b3;
    font-size: 14px;
    font-weight: 700;
    margin: 22px 0;
}

.divider::before,
.divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background-color: #d0d5dd;
}


/* ---------- Form ---------- */

.form-label {
    text-align: center;
    font-size: 16px;
    font-weight: 700;
    color: #344054;
    margin-bottom: 8px;
}

div[data-testid="stTextInput"] input {
    font-size: 20px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 14px;
    border-radius: 10px;
}

div[data-testid="stTextInput"] input::placeholder {
    text-transform: none;
    letter-spacing: normal;
}

div[data-testid="stFormSubmitButton"] button {
    height: 52px;
    width: 100%;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 700;
    background-color: #0460A9;
    color: #ffffff;
    border: none;
    margin-top: 6px;
}

div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:focus {
    background-color: #034a83;
    color: #ffffff;
    border: none;
}


/* ---------- Result cards ---------- */

.result-card {
    margin-top: 24px;
    padding: 28px 20px;
    border-radius: 18px;
    text-align: center;
    animation: fadeIn 0.25s ease-out;
}

.result-card.ok {
    background-color: #ecfdf3;
    border: 3px solid #12b76a;
    color: #067647;
}

.result-card.bad {
    background-color: #fef3f2;
    border: 3px solid #f04438;
    color: #b42318;
}

.result-icon {
    font-size: 52px;
    font-weight: 800;
    line-height: 1;
}

.result-title {
    font-size: 32px;
    font-weight: 800;
    margin-top: 10px;
}

.result-text {
    font-size: 16px;
    margin-top: 6px;
}

.result-id {
    font-size: 14px;
    margin-top: 10px;
    opacity: 0.8;
    font-family: monospace;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: none; }
}


/* ---------- Footer ---------- */

.footer-text {
    text-align: center;
    color: #98a2b3;
    font-size: 12px;
    margin-top: 36px;
}


/* ---------- Mobile ---------- */

@media (max-width: 600px) {

    .block-container {
        padding-left: 16px;
        padding-right: 16px;
    }

    .main-title {
        font-size: 28px;
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
# GENERATE QR (as base64 for pixel-perfect centering)
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
    f'<div class="main-title">EVENT CHECK-IN</div>'
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
        f'<div class="divider">OR</div>',
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
        placeholder="e.g. DEVABSA1",
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
    '<div class="footer-text">Event Registration Verification</div>',
    unsafe_allow_html=True,
)
