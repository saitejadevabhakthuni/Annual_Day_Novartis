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

/* ============================================================
   PREMIUM EVENT CHECK-IN UI
   Theme: Classic Black, Silver, Orange Gold
   ============================================================ */


/* ---------- Hide Streamlit default elements ---------- */

#MainMenu,
footer,
header {
    visibility: hidden;
}

div[data-testid="InputInstructions"] {
    display: none;
}


/* ---------- Global page background ---------- */

.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 122, 0, 0.22), transparent 32%),
        radial-gradient(circle at bottom right, rgba(210, 214, 220, 0.20), transparent 30%),
        linear-gradient(145deg, #050505 0%, #111111 38%, #24272c 72%, #8a8d93 100%) !important;
    background-attachment: fixed !important;
    color: #ffffff;
}


/* ---------- Premium top accent ---------- */

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 7px;
    background: linear-gradient(
        90deg,
        #ff5f00,
        #ff9f1c,
        #ffd089,
        #ff9f1c,
        #ff5f00
    );
    z-index: 9999;
    box-shadow: 0 0 22px rgba(255, 139, 24, 0.65);
}


/* ---------- Page container ---------- */

.block-container {
    max-width: 560px;
    padding-top: 3rem;
    padding-bottom: 2.5rem;
}


/* ---------- Header ---------- */

.main-title {
    text-align: center;
    font-size: 36px;
    font-weight: 950;
    letter-spacing: 1.4px;
    line-height: 1.15;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #ffffff 0%, #ffb347 45%, #ff6a00 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 10px 30px rgba(255, 122, 0, 0.20);
}

.subtitle {
    text-align: center;
    color: #d4d7dc;
    font-size: 15.5px;
    font-weight: 500;
    margin-bottom: 28px;
    letter-spacing: 0.3px;
}


/* ---------- Shared premium card ---------- */

.qr-card,
div[data-testid="stForm"] {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(215, 219, 225, 0.96)),
        linear-gradient(145deg, #f7f8fa, #c7cbd3) !important;
    border: 1.8px solid rgba(255, 154, 36, 0.95) !important;
    border-radius: 26px !important;
    box-shadow:
        0 18px 45px rgba(0, 0, 0, 0.38),
        0 8px 30px rgba(255, 122, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    padding: 28px !important;
}

.qr-card::before,
div[data-testid="stForm"]::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(
            120deg,
            rgba(255, 255, 255, 0.45),
            transparent 35%,
            transparent 70%,
            rgba(255, 154, 36, 0.18)
        );
    pointer-events: none;
}


/* ---------- QR Card ---------- */

.qr-card {
    text-align: center;
    animation: cardIn 0.35s ease-out;
}

.qr-card img {
    width: 210px;
    max-width: 72%;
    height: auto;
    display: block;
    margin: 0 auto;
    padding: 12px;
    background-color: #ffffff;
    border: 4px solid #111111;
    border-radius: 18px;
    box-shadow:
        0 12px 28px rgba(0, 0, 0, 0.28),
        0 0 0 6px rgba(255, 122, 0, 0.12);
}

.qr-title {
    font-size: 19px;
    font-weight: 950;
    color: #111111;
    margin-top: 18px;
    letter-spacing: 0.8px;
}

.qr-description {
    color: #4b4f56;
    font-size: 14px;
    font-weight: 500;
    margin-top: 6px;
}


/* ---------- Divider ---------- */

.divider {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 28px 0;
}

.divider::before,
.divider::after {
    content: "";
    flex: 1;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.65), transparent);
}

.divider span {
    background: linear-gradient(135deg, #ff6a00, #ffb347);
    color: #080808;
    font-size: 13px;
    font-weight: 950;
    padding: 7px 18px;
    border-radius: 999px;
    letter-spacing: 1px;
    box-shadow:
        0 0 18px rgba(255, 122, 0, 0.55),
        inset 0 1px 0 rgba(255, 255, 255, 0.45);
}


/* ---------- Form ---------- */

div[data-testid="stForm"] {
    animation: cardIn 0.35s ease-out;
}

.form-label {
    text-align: center;
    font-size: 17px;
    font-weight: 900;
    color: #111111;
    margin-bottom: 12px;
    letter-spacing: 0.3px;
}


/* Text input wrapper */

div[data-testid="stTextInput"] {
    margin-top: 4px;
}

div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border-radius: 16px !important;
}

div[data-testid="stTextInput"] div[data-baseweb="input"] {
    border: 2px solid #111111 !important;
    box-shadow:
        inset 0 1px 2px rgba(0, 0, 0, 0.08),
        0 8px 18px rgba(0, 0, 0, 0.10);
}

div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: #ff7a00 !important;
    box-shadow:
        0 0 0 4px rgba(255, 122, 0, 0.25),
        0 10px 22px rgba(255, 122, 0, 0.16);
}

div[data-testid="stTextInput"] input {
    font-size: 21px;
    font-weight: 850;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 16px 14px;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    background-color: #ffffff !important;
    caret-color: #ff7a00;
}

div[data-testid="stTextInput"] input::placeholder {
    text-transform: none;
    letter-spacing: normal;
    font-weight: 450;
    color: #9a9da4 !important;
    -webkit-text-fill-color: #9a9da4 !important;
}


/* Submit button */

div[data-testid="stFormSubmitButton"] button {
    height: 58px;
    width: 100%;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #ff5f00 0%, #ff9f1c 50%, #ffd089 100%) !important;
    color: #050505 !important;
    border: 2px solid #050505 !important;
    margin-top: 12px;
    box-shadow:
        0 12px 26px rgba(255, 106, 0, 0.38),
        inset 0 1px 0 rgba(255, 255, 255, 0.48);
    transition: all 0.18s ease;
}

div[data-testid="stFormSubmitButton"] button p {
    font-size: 18px !important;
    font-weight: 950 !important;
    letter-spacing: 1.4px;
}

div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:focus {
    background: linear-gradient(135deg, #080808, #1b1b1b) !important;
    color: #ffb347 !important;
    border: 2px solid #ff8a00 !important;
    transform: translateY(-2px);
    box-shadow:
        0 16px 32px rgba(255, 106, 0, 0.36),
        0 0 0 4px rgba(255, 122, 0, 0.18);
}

div[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(1px);
}


/* ---------- Alerts ---------- */

div[data-testid="stAlert"] {
    border-radius: 16px !important;
    border: 1px solid rgba(255, 154, 36, 0.55) !important;
}


/* ---------- Result cards ---------- */

.result-card {
    position: relative;
    overflow: hidden;
    margin-top: 28px;
    padding: 32px 22px;
    border-radius: 24px;
    text-align: center;
    color: #ffffff;
    animation: resultIn 0.35s ease-out;
}

.result-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at top left, rgba(255, 255, 255, 0.25), transparent 35%),
        linear-gradient(120deg, rgba(255, 255, 255, 0.14), transparent 55%);
    pointer-events: none;
}

.result-card.ok {
    background: linear-gradient(135deg, #043d24 0%, #079455 48%, #12b76a 100%);
    border: 2px solid rgba(182, 255, 215, 0.85);
    box-shadow:
        0 18px 42px rgba(18, 183, 106, 0.36),
        0 0 0 5px rgba(18, 183, 106, 0.12);
}

.result-card.bad {
    background: linear-gradient(135deg, #610909 0%, #c81e1e 52%, #f04438 100%);
    border: 2px solid rgba(255, 202, 202, 0.85);
    box-shadow:
        0 18px 42px rgba(240, 68, 56, 0.36),
        0 0 0 5px rgba(240, 68, 56, 0.12);
}

.result-icon {
    position: relative;
    z-index: 1;
    width: 76px;
    height: 76px;
    margin: 0 auto;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 46px;
    font-weight: 950;
    line-height: 1;
    background: rgba(0, 0, 0, 0.22);
    border: 2px solid rgba(255, 255, 255, 0.65);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.24);
}

.result-title {
    position: relative;
    z-index: 1;
    font-size: 34px;
    font-weight: 950;
    margin-top: 16px;
    letter-spacing: 1.4px;
}

.result-text {
    position: relative;
    z-index: 1;
    font-size: 16px;
    margin-top: 8px;
    font-weight: 500;
}

.result-id {
    position: relative;
    z-index: 1;
    display: inline-block;
    font-size: 14px;
    margin-top: 16px;
    padding: 6px 14px;
    border-radius: 999px;
    background-color: rgba(0, 0, 0, 0.34);
    border: 1px solid rgba(255, 255, 255, 0.26);
    font-family: monospace;
    letter-spacing: 0.5px;
}


/* ---------- Footer ---------- */

.footer-text {
    text-align: center;
    color: #d2d5da;
    font-size: 12px;
    margin-top: 38px;
    letter-spacing: 0.7px;
    opacity: 0.95;
}

.footer-text span {
    color: #ffb347;
    font-weight: 850;
}


/* ---------- Animations ---------- */

@keyframes cardIn {
    from {
        opacity: 0;
        transform: translateY(12px) scale(0.985);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes resultIn {
    from {
        opacity: 0;
        transform: translateY(14px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}


/* ---------- Mobile ---------- */

@media (max-width: 600px) {

    .block-container {
        padding-left: 16px;
        padding-right: 16px;
        padding-top: 2.4rem;
    }

    .main-title {
        font-size: 29px;
        letter-spacing: 0.7px;
    }

    .subtitle {
        font-size: 14.5px;
        margin-bottom: 22px;
    }

    .qr-card,
    div[data-testid="stForm"] {
        border-radius: 22px !important;
        padding: 22px !important;
    }

    .qr-card img {
        width: 190px;
    }

    div[data-testid="stTextInput"] input {
        font-size: 19px;
        padding: 14px 12px;
    }

    div[data-testid="stFormSubmitButton"] button {
        height: 56px;
    }

    .result-title {
        font-size: 29px;
    }

    .result-icon {
        width: 68px;
        height: 68px;
        font-size: 40px;
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
