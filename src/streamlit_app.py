import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
AUDIT_FILE = "data/processed/agent_audit_log.jsonl"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RevenueOS-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1500px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(128,128,128,.08),
            rgba(128,128,128,.025)
        );
        margin-bottom: 1.2rem;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 750;
        margin-bottom: .15rem;
        letter-spacing: -.5px;
    }

    .hero-subtitle {
        color: rgba(128,128,128,.95);
        font-size: 1rem;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: .72rem;
        font-weight: 700;
        color: rgba(128,128,128,.9);
        margin-bottom: .35rem;
    }


    .workflow {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .25rem;
        padding: .85rem 1rem;
        margin: .7rem 0 1.15rem 0;
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 14px;
        background: rgba(128,128,128,.025);
    }

    .workflow-step {
        flex: 1;
        text-align: center;
        font-size: .74rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .workflow-number {
        display: inline-flex;
        width: 25px;
        height: 25px;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: .25rem;
        font-size: .72rem;
    }

    .workflow-arrow {
        color: rgba(128,128,128,.65);
        font-size: .95rem;
        flex: 0 0 auto;
    }

    .queue-header {
        margin-bottom: .45rem;
    }

    .queue-title {
        font-size: 1.25rem;
        font-weight: 750;
        margin-bottom: .15rem;
    }

    .queue-subtitle {
        color: rgba(128,128,128,.85);
        font-size: .82rem;
    }

    .risk-banner {
        padding: 1.1rem 1.25rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 80, 80, .30);
        background: rgba(255, 80, 80, .07);
        margin: .5rem 0 1.2rem 0;
    }

    .risk-banner-title {
        font-size: 1.35rem;
        font-weight: 750;
    }

    .risk-banner-text {
        margin-top: .25rem;
        color: rgba(128,128,128,.95);
    }

    .evidence-card {
        min-height: 165px;
        padding: 1.05rem;
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 14px;
        background: rgba(128,128,128,.035);
    }

    .evidence-label {
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: .72rem;
        font-weight: 700;
        color: rgba(128,128,128,.9);
        margin-bottom: .55rem;
    }

    .evidence-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: .5rem;
    }

    .evidence-source {
        font-size: .78rem;
        color: rgba(128,128,128,.85);
    }

    .case-strip {
        padding: 1rem 1.15rem;
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 12px;
        background: rgba(128,128,128,.035);
    }

    .review-panel {
        padding: 1.2rem;
        border: 1px solid rgba(255, 180, 0, .35);
        border-radius: 14px;
        background: rgba(255, 180, 0, .06);
    }

    .review-title {
        font-size: 1.3rem;
        font-weight: 750;
    }

    .timeline-item {
        padding: .75rem 1rem;
        margin-bottom: .45rem;
        border-left: 3px solid rgba(128,128,128,.35);
        background: rgba(128,128,128,.035);
        border-radius: 0 9px 9px 0;
    }

    .timeline-event {
        font-weight: 700;
        font-size: .92rem;
    }

    .timeline-time {
        font-size: .75rem;
        color: rgba(128,128,128,.85);
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 12px;
        padding: 14px;
        background: rgba(128,128,128,.035);
    }

    div[data-testid="stMetricValue"] {
        font-weight: 750;
    }

    .stButton > button {
        min-height: 42px;
        border-radius: 8px;
        font-weight: 650;
    }

    div[data-testid="stExpander"] {
        border-radius: 10px;
    }

    h1, h2, h3 {
        letter-spacing: -.25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def load_audit_events(merchant_id):
    events = []

    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    event = json.loads(line)

                    if str(event.get("merchant_id", "")).upper() == str(
                        merchant_id
                    ).upper():
                        events.append(event)

                except json.JSONDecodeError:
                    continue

    except FileNotFoundError:
        return []

    return events


def get_cases():
    try:
        response = requests.get(f"{API_URL}/cases", timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get("cases", [])

        return []

    except Exception:
        return []


def get_case(case_id):
    try:
        response = requests.get(
            f"{API_URL}/cases/{case_id}",
            timeout=15,
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Case API returned HTTP {response.status_code}"
        )
        return None

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to FastAPI. Make sure the API server is running."
        )
        return None

    except requests.exceptions.Timeout:
        st.error("The case request timed out.")
        return None

    except Exception as exc:
        st.error(f"Unexpected case retrieval error: {exc}")
        return None


def process_case_review(case, decision, reviewer, comments):
    review_id = case.get("review_id")
    merchant_id = case.get("merchant_id")

    if not review_id:
        st.error("This case does not have a valid review ID.")
        return None

    payload = {
        "merchant_id": merchant_id,
        "review_id": review_id,
        "reviewer": reviewer,
        "comments": comments,
    }

    try:
        response = requests.post(
            f"{API_URL}/review/{review_id}/{decision}",
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Review API returned HTTP {response.status_code}"
        )
        st.code(response.text)
        return None

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to FastAPI.")
        return None

    except requests.exceptions.Timeout:
        st.error("The review request timed out.")
        return None

    except Exception as exc:
        st.error(f"Unexpected review error: {exc}")
        return None


def get_latest_cases(cases):
    latest = {}

    for case in cases:
        merchant_id = str(case.get("merchant_id", "")).strip().upper()

        if not merchant_id:
            continue

        current = latest.get(merchant_id)

        if current is None:
            latest[merchant_id] = case
            continue

        current_time = current.get(
            "updated_at",
            current.get("created_at", ""),
        )

        new_time = case.get(
            "updated_at",
            case.get("created_at", ""),
        )

        if new_time >= current_time:
            latest[merchant_id] = case

    return list(latest.values())


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_timestamp(value):
    if not value:
        return "N/A"

    try:
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%d %b %Y • %H:%M:%S")
    except Exception:
        return str(value)


def filter_case_audit_events(audit_events, case):
    if not case:
        return audit_events

    case_id = case.get("case_id")
    review_id = case.get("review_id")

    linked = []

    for event in audit_events:
        details = event.get("details", {})

        if not isinstance(details, dict):
            details = {}

        event_case_id = details.get("case_id")
        event_review_id = details.get("review_id")

        if case_id and event_case_id == case_id:
            linked.append(event)
            continue

        if review_id and event_review_id == review_id:
            if event not in linked:
                linked.append(event)

    return linked if linked else audit_events


def render_status_badge(label, value):
    value = str(value or "N/A").upper()

    if value in {"CRITICAL", "ESCALATE", "REJECTED"}:
        st.error(f"**{label}:** {value}")
    elif value in {"HIGH", "PENDING_HUMAN_REVIEW", "PENDING", "ON_HOLD"}:
        st.warning(f"**{label}:** {value}")
    elif value in {"APPROVED", "LOW", "NO_ACTION"}:
        st.success(f"**{label}:** {value}")
    else:
        st.info(f"**{label}:** {value}")


def render_evidence_card(title, finding, source, symbol):
    st.markdown(
        f"""
        <div class="evidence-card">
            <div class="evidence-label">{symbol} {title}</div>
            <div class="evidence-title">{finding}</div>
            <div class="evidence-source">Source: {source}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI-Powered Risk Operations</div>
        <div class="hero-title">RevenueOS-AI</div>
        <div class="hero-subtitle">
            Autonomous Merchant Risk Investigation & Human Review Platform
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

operations_tab, investigation_tab = st.tabs(
    [
        "Operations Dashboard",
        "Merchant Investigation",
    ]
)


# =========================================================
# OPERATIONS DASHBOARD
# =========================================================

with operations_tab:
    st.header("Risk Operations Dashboard")
    st.caption(
        "Detect merchant risk, investigate failure patterns, "
        "and control high-risk actions through human review."
    )

    cases = get_cases()
    latest_cases = get_latest_cases(cases)

    if not cases:
        st.warning("No investigation cases found.")
    else:
        # -----------------------------------------------------
        # KPI CARDS
        # -----------------------------------------------------

        total_merchants = len(latest_cases)

        pending_reviews = sum(
            1
            for case in latest_cases
            if str(case.get("status", "")).upper()
            == "PENDING_HUMAN_REVIEW"
        )

        open_cases = sum(
            1
            for case in latest_cases
            if str(case.get("status", "")).upper() == "OPEN"
        )

        approved_cases = sum(
            1
            for case in latest_cases
            if str(case.get("status", "")).upper() == "APPROVED"
        )

        rejected_cases = sum(
            1
            for case in latest_cases
            if str(case.get("status", "")).upper() == "REJECTED"
        )

        critical_merchants = sum(
            1
            for case in latest_cases
            if str(case.get("risk_category", "")).upper() == "CRITICAL"
        )

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.metric("Merchants", total_merchants)

        with col2:
            st.metric("Critical", critical_merchants)

        with col3:
            st.metric("Pending Review", pending_reviews)

        with col4:
            st.metric("Active Cases", open_cases)

        with col5:
            st.metric("Approved", approved_cases)

        with col6:
            st.metric("Rejected", rejected_cases)

        st.markdown(
            """
            <div class="workflow">
                <div class="workflow-step">
                    <div class="workflow-number">1</div>
                    Risk Assessment
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">2</div>
                    AI Decision
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">3</div>
                    Investigation
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">4</div>
                    Action
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">5</div>
                    Human Review
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">6</div>
                    Audit
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # -----------------------------------------------------
        # PRIORITY RISK QUEUE
        # -----------------------------------------------------

        def calculate_priority(case):
            risk_category = str(
                case.get("risk_category", "")
            ).upper()

            status = str(
                case.get("status", "")
            ).upper()

            action = str(
                case.get("recommended_action")
                or case.get("decision")
                or ""
            ).upper()

            risk_score = safe_float(
                case.get("risk_score", 0)
            )

            priority = risk_score

            if status == "PENDING_HUMAN_REVIEW":
                priority += 1000

            priority += {
                "CRITICAL": 400,
                "HIGH": 300,
                "MEDIUM": 200,
                "LOW": 100,
            }.get(risk_category, 0)

            priority += {
                "ESCALATE": 100,
                "INVESTIGATE": 75,
                "MONITOR": 25,
            }.get(action, 0)

            return priority

        priority_cases = sorted(
            latest_cases,
            key=calculate_priority,
            reverse=True,
        )

        st.markdown(
            """
            <div class="queue-header">
                <div class="section-kicker">Attention Queue</div>
                <div class="queue-title">Priority Risk Queue</div>
                <div class="queue-subtitle">
                    Highest-risk merchants requiring attention first.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        priority_preview = []

        for case in priority_cases[:5]:
            priority_preview.append(
                {
                    "Merchant": case.get(
                        "merchant_id",
                        "N/A",
                    ),
                    "Risk Score": round(
                        safe_float(
                            case.get(
                                "risk_score",
                                0,
                            )
                        ),
                        2,
                    ),
                    "Category": case.get(
                        "risk_category",
                        "N/A",
                    ),
                    "Action": (
                        case.get("recommended_action")
                        or case.get("decision")
                        or "N/A"
                    ),
                    "Status": case.get(
                        "status",
                        "N/A",
                    ),
                }
            )

        if priority_preview:
            st.dataframe(
                pd.DataFrame(priority_preview),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No priority risk cases available.")

        st.divider()

        # -----------------------------------------------------
        # FILTERS
        # -----------------------------------------------------

        st.subheader("Risk Filters")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            selected_risk = st.selectbox(
                "Risk Category",
                [
                    "All",
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                ],
                key="ops_risk_filter",
            )

        with filter_col2:
            selected_status = st.selectbox(
                "Case Status",
                [
                    "All",
                    "PENDING_HUMAN_REVIEW",
                    "OPEN",
                    "APPROVED",
                    "REJECTED",
                    "ON_HOLD",
                ],
                key="ops_status_filter",
            )

        with filter_col3:
            selected_action = st.selectbox(
                "Recommended Action",
                [
                    "All",
                    "ESCALATE",
                    "INVESTIGATE",
                    "MONITOR",
                    "NO_ACTION",
                ],
                key="ops_action_filter",
            )

        filtered_cases = latest_cases.copy()

        if selected_risk != "All":
            filtered_cases = [
                case
                for case in filtered_cases
                if str(
                    case.get("risk_category", "")
                ).upper()
                == selected_risk.upper()
            ]

        if selected_status != "All":
            filtered_cases = [
                case
                for case in filtered_cases
                if str(
                    case.get("status", "")
                ).upper()
                == selected_status.upper()
            ]

        if selected_action != "All":
            filtered_cases = [
                case
                for case in filtered_cases
                if str(
                    case.get("recommended_action")
                    or case.get("decision")
                    or ""
                ).upper()
                == selected_action.upper()
            ]

        filtered_cases = sorted(
            filtered_cases,
            key=calculate_priority,
            reverse=True,
        )

        # -----------------------------------------------------
        # FILTERED QUEUE
        # -----------------------------------------------------

        st.subheader("Filtered Risk Queue")
        st.caption(
            "Cases are ranked using risk severity, recommended action, "
            "and human-review urgency."
        )

        table_data = []

        for case in filtered_cases:
            table_data.append(
                {
                    "Merchant": case.get(
                        "merchant_id",
                        "N/A",
                    ),
                    "Risk Score": round(
                        safe_float(
                            case.get(
                                "risk_score",
                                0,
                            )
                        ),
                        2,
                    ),
                    "Risk Category": case.get(
                        "risk_category",
                        "N/A",
                    ),
                    "Priority": round(
                        calculate_priority(case),
                        2,
                    ),
                    "Action": (
                        case.get("recommended_action")
                        or case.get("decision")
                        or "N/A"
                    ),
                    "Case Status": case.get(
                        "status",
                        "N/A",
                    ),
                    "Review": case.get(
                        "review_status",
                        "N/A",
                    ),
                    "Case ID": case.get(
                        "case_id",
                        "N/A",
                    ),
                }
            )

        df = pd.DataFrame(table_data)

        if not df.empty:
            df = df.sort_values(
                by=["Priority", "Risk Score"],
                ascending=[False, False],
            )

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
            )
        else:
            st.info(
                "No cases match the selected filters."
            )

        st.caption(
            f"{len(filtered_cases)} cases shown • "
            f"{len(latest_cases)} latest cases • "
            f"{len(cases)} total stored cases"
        )

        st.divider()

        # -----------------------------------------------------
        # CASE DETAILS
        # -----------------------------------------------------

        st.divider()
        st.subheader("Case Details & Human Review")
        st.caption(
            "Opening a stored case does not run a new investigation."
        )

        if filtered_cases:
            case_options = [
                case.get("case_id")
                for case in filtered_cases
                if case.get("case_id")
            ]

            selected_case_id = st.selectbox(
                "Select Case",
                case_options,
                key="selected_case_id",
            )

            selected_case = get_case(selected_case_id)

            if selected_case:
                risk_score = safe_float(
                    selected_case.get("risk_score")
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Merchant",
                        selected_case.get(
                            "merchant_id",
                            "N/A",
                        ),
                    )

                with col2:
                    st.metric(
                        "Risk Score",
                        f"{risk_score:.2f}",
                    )

                with col3:
                    st.metric(
                        "Risk Category",
                        selected_case.get(
                            "risk_category",
                            "N/A",
                        ),
                    )

                with col4:
                    st.metric(
                        "Case Status",
                        selected_case.get(
                            "status",
                            "N/A",
                        ),
                    )

                st.markdown(
                    f"""
                    <div class="case-strip">
                        <b>Case:</b> {selected_case.get("case_id", "N/A")}
                        &nbsp;&nbsp; | &nbsp;&nbsp;
                        <b>Action:</b> {selected_case.get("recommended_action", "N/A")}
                        &nbsp;&nbsp; | &nbsp;&nbsp;
                        <b>Review:</b> {selected_case.get("review_status", "N/A")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                findings = selected_case.get("findings", [])

                if findings:
                    st.write("")
                    st.markdown("**Investigation Evidence**")

                    for finding in findings:
                        if isinstance(finding, dict):
                            st.write(
                                f"• {finding.get('finding', str(finding))}"
                            )
                        else:
                            st.write(f"• {finding}")

                # -------------------------------------------------
                # EXISTING CASE REVIEW
                # -------------------------------------------------

                if (
                    selected_case.get("status")
                    == "PENDING_HUMAN_REVIEW"
                    and selected_case.get("review_id")
                ):
                    st.divider()

                    st.markdown(
                        """
                        <div class="review-panel">
                            <div class="eyebrow">Human-in-the-Loop</div>
                            <div class="review-title">
                                Human Review Required
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    review_id = selected_case.get("review_id")

                    st.code(review_id)

                    reviewer = st.text_input(
                        "Reviewer Name",
                        value="Demo Reviewer",
                        key=f"ops_reviewer_{selected_case_id}",
                    )

                    comments = st.text_area(
                        "Review Comments",
                        value=(
                            "Investigation evidence supports "
                            "the recommended action."
                        ),
                        key=f"ops_comments_{selected_case_id}",
                    )

                    review_col1, review_col2, review_col3 = st.columns(3)

                    with review_col1:
                        if st.button(
                            "APPROVE",
                            type="primary",
                            width="stretch",
                            key=f"ops_approve_{selected_case_id}",
                        ):
                            result = process_case_review(
                                selected_case,
                                "approve",
                                reviewer,
                                comments,
                            )

                            if result:
                                st.session_state[
                                    "operations_review_result"
                                ] = result
                                st.rerun()

                    with review_col2:
                        if st.button(
                            "REJECT",
                            width="stretch",
                            key=f"ops_reject_{selected_case_id}",
                        ):
                            result = process_case_review(
                                selected_case,
                                "reject",
                                reviewer,
                                comments,
                            )

                            if result:
                                st.session_state[
                                    "operations_review_result"
                                ] = result
                                st.rerun()

                    with review_col3:
                        if st.button(
                            "HOLD",
                            width="stretch",
                            key=f"ops_hold_{selected_case_id}",
                        ):
                            result = process_case_review(
                                selected_case,
                                "hold",
                                reviewer,
                                comments,
                            )

                            if result:
                                st.session_state[
                                    "operations_review_result"
                                ] = result
                                st.rerun()

                elif selected_case.get("status") == "APPROVED":
                    st.success("This case has already been approved.")

                elif selected_case.get("status") == "REJECTED":
                    st.error("This case has already been rejected.")

                elif selected_case.get("status") == "ON_HOLD":
                    st.warning("This case is currently on hold.")

                else:
                    st.info("No human review is required for this case.")

                # -------------------------------------------------
                # REVIEW RESULT
                # -------------------------------------------------

                if "operations_review_result" in st.session_state:
                    review_result = st.session_state[
                        "operations_review_result"
                    ]

                    st.divider()
                    st.subheader("Latest Review Result")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Decision",
                            review_result.get(
                                "review_decision",
                                "N/A",
                            ),
                        )

                    with col2:
                        st.metric(
                            "Case Status",
                            review_result.get(
                                "case_status",
                                "N/A",
                            ),
                        )

                    with col3:
                        st.metric(
                            "Review Status",
                            review_result.get(
                                "review_status",
                                "N/A",
                            ),
                        )

        else:
            st.info("No cases match the selected filters.")

        st.divider()
        st.caption(
            f"{len(filtered_cases)} cases shown • "
            f"{len(latest_cases)} latest cases • "
            f"{len(cases)} total stored cases"
        )


# =========================================================
# MERCHANT INVESTIGATION
# =========================================================

with investigation_tab:
    st.header("Merchant Investigation")
    st.caption(
        "Run an AI-assisted investigation and, when required, "
        "route the decision to a human reviewer."
    )

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    merchant_id = st.sidebar.text_input(
        "Merchant ID",
        value="M00005",
    ).strip().upper()

    st.sidebar.caption(
        "Try M00005 for a Critical → Escalate → Human Review demo."
    )

    st.sidebar.divider()

    st.sidebar.markdown("**AI Risk Workflow**")
    st.sidebar.caption(
        "Detect risk → explain the decision → investigate evidence → "
        "recommend action → route high-risk cases to human review → audit."
    )

    run_investigation = st.sidebar.button(
        "Run Investigation",
        type="primary",
        width="stretch",
    )

    # -----------------------------------------------------
    # RUN INVESTIGATION
    # -----------------------------------------------------

    if run_investigation:
        if not merchant_id:
            st.error("Please enter a merchant ID.")
        else:
            with st.spinner(
                f"Running investigation for {merchant_id}..."
            ):
                try:
                    response = requests.get(
                        f"{API_URL}/merchant/{merchant_id}",
                        timeout=30,
                    )

                    if response.status_code == 200:
                        st.session_state["result"] = response.json()
                        st.session_state.pop(
                            "review_result",
                            None,
                        )
                        st.success(
                            "Investigation completed successfully."
                        )

                    else:
                        st.error(
                            f"API Error: {response.status_code}"
                        )
                        st.code(response.text)

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to FastAPI. "
                        "Make sure the API server is running."
                    )

                except requests.exceptions.Timeout:
                    st.error("The API request timed out.")

                except Exception as exc:
                    st.error(f"Unexpected error: {exc}")

    # -----------------------------------------------------
    # DISPLAY INVESTIGATION
    # -----------------------------------------------------

    if "result" not in st.session_state:
        st.info(
            "Enter a merchant ID in the sidebar and click "
            "**Run Investigation**."
        )

    else:
        result = st.session_state["result"]

        risk_score = safe_float(
            result.get("risk_score"),
            0,
        )

        risk_category = str(
            result.get("risk_category", "N/A")
        )

        decision = str(
            result.get("decision", "N/A")
        )

        failure_rate = result.get("failure_rate")

        if isinstance(failure_rate, (int, float)):
            failure_rate_display = f"{failure_rate * 100:.2f}%"
        else:
            failure_rate_display = "N/A"

        # -------------------------------------------------
        # AI WORKFLOW
        # -------------------------------------------------

        st.markdown(
            """
            <div class="workflow">
                <div class="workflow-step">
                    <div class="workflow-number">1</div>
                    Risk
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">2</div>
                    Decision
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">3</div>
                    Evidence
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">4</div>
                    Action
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">5</div>
                    Review
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="workflow-number">6</div>
                    Audit
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # RISK BANNER
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="risk-banner">
                <div class="eyebrow">Investigation Completed</div>
                <div class="risk-banner-title">
                    {risk_category} Risk • {decision}
                </div>
                <div class="risk-banner-text">
                    RevenueOS-AI evaluated merchant
                    <b>{result.get("merchant_id", merchant_id)}</b>
                    and generated an automated risk decision.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # RISK OVERVIEW
        # -------------------------------------------------

        st.subheader("Merchant Risk Overview")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Merchant",
                result.get("merchant_id", merchant_id),
            )

        with col2:
            st.metric(
                "Risk Score",
                f"{risk_score:.2f}",
            )

        with col3:
            st.metric(
                "Risk Category",
                risk_category,
            )

        with col4:
            st.metric(
                "Failure Rate",
                failure_rate_display,
            )

        with col5:
            st.metric(
                "Decision",
                decision,
            )

        # -------------------------------------------------
        # DECISION REASON
        # -------------------------------------------------

        st.divider()
        st.subheader("Why did the AI make this decision?")

        st.info(
            result.get(
                "reason",
                "No decision reason available.",
            )
        )

        # -------------------------------------------------
        # INVESTIGATION EVIDENCE
        # -------------------------------------------------

        findings = result.get("findings", [])

        st.divider()
        st.header("Automated Investigation")
        st.caption(
            "Supporting evidence identified by RevenueOS-AI."
        )

        if findings:
            evidence_columns = st.columns(
                min(len(findings), 3)
            )

            for index, finding in enumerate(findings):
                if not isinstance(finding, dict):
                    finding = {
                        "finding": str(finding),
                        "source": "investigation",
                        "type": "evidence",
                    }

                finding_type = finding.get(
                    "type",
                    "evidence",
                )

                if finding_type == "failure_pattern":
                    title = "Failure Pattern"
                    symbol = "⚠"
                elif finding_type == "payment_method_pattern":
                    title = "Payment Method"
                    symbol = "↗"
                elif finding_type == "time_pattern":
                    title = "Time Pattern"
                    symbol = "◷"
                else:
                    title = "Investigation Evidence"
                    symbol = "•"

                with evidence_columns[index % len(evidence_columns)]:
                    render_evidence_card(
                        title,
                        finding.get(
                            "finding",
                            "N/A",
                        ),
                        finding.get(
                            "source",
                            "N/A",
                        ),
                        symbol,
                    )

        else:
            st.info(
                "No supporting investigation findings were returned."
            )

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        confidence = result.get("confidence", {})

        if confidence:
            st.divider()
            st.subheader("Investigation Confidence")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Confidence Score",
                    f"{safe_float(confidence.get('score', 0)):.0f}%",
                )

            with col2:
                st.metric(
                    "Confidence Level",
                    confidence.get(
                        "category",
                        "N/A",
                    ),
                )

            with col3:
                st.metric(
                    "Evidence Findings",
                    confidence.get(
                        "finding_count",
                        len(findings),
                    ),
                )

        # -------------------------------------------------
        # ACTION
        # -------------------------------------------------

        st.divider()
        st.header("AI Recommended Action")

        action = (
            result.get("recommended_action")
            or result.get("decision")
            or "N/A"
        )

        human_required = result.get(
            "human_approval_required",
            False,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Recommended Action",
                action,
            )

        with col2:
            st.metric(
                "Human Approval Required",
                "YES" if human_required else "NO",
            )

        # -------------------------------------------------
        # CASE
        # -------------------------------------------------

        case = result.get("case")

        if case:
            st.divider()
            st.header("Investigation Case")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.caption("CASE ID")
                st.code(
                    case.get(
                        "case_id",
                        "N/A",
                    )
                )

            with col2:
                st.caption("CASE STATUS")
                render_status_badge(
                    "Status",
                    case.get(
                        "status",
                        "N/A",
                    ),
                )

            with col3:
                st.caption("REVIEW STATUS")
                render_status_badge(
                    "Review",
                    case.get(
                        "review_status",
                        "N/A",
                    ),
                )

        # -------------------------------------------------
        # HUMAN REVIEW
        # -------------------------------------------------

        review = result.get("review")

        if (
            review
            and review.get("status") == "PENDING"
        ):
            st.divider()

            st.markdown(
                """
                <div class="review-panel">
                    <div class="eyebrow">Human-in-the-Loop Control</div>
                    <div class="review-title">
                        Human Review Required
                    </div>
                    <div>
                        AI has completed the investigation.
                        A reviewer must approve, reject, or hold the
                        recommended action.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

            review_id = review.get(
                "review_id",
                "",
            )

            col1, col2 = st.columns(2)

            with col1:
                st.caption("REVIEW ID")
                st.code(review_id)

            with col2:
                st.caption("AI DECISION")
                st.metric(
                    "Recommended Decision",
                    review.get(
                        "decision",
                        "N/A",
                    ),
                )

            reviewer = st.text_input(
                "Reviewer Name",
                value="Demo Reviewer",
                key="investigation_reviewer",
            )

            comments = st.text_area(
                "Review Comments",
                value=(
                    "Investigation evidence supports "
                    "the recommended action."
                ),
                key="investigation_comments",
            )

            st.write("### Review Decision")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "APPROVE",
                    type="primary",
                    width="stretch",
                    key="investigation_approve",
                ):
                    payload = {
                        "merchant_id": merchant_id,
                        "review_id": review_id,
                        "reviewer": reviewer,
                        "comments": comments,
                    }

                    try:
                        response = requests.post(
                            f"{API_URL}/review/{review_id}/approve",
                            json=payload,
                            timeout=30,
                        )

                        if response.status_code == 200:
                            st.session_state[
                                "review_result"
                            ] = response.json()

                            # Refresh the stored case in the result.
                            updated_case = get_case(
                                case.get("case_id")
                            )

                            if updated_case:
                                st.session_state["result"][
                                    "case"
                                ] = updated_case

                            st.rerun()

                        else:
                            st.error(response.text)

                    except Exception as exc:
                        st.error(
                            f"Approval error: {exc}"
                        )

            with col2:
                if st.button(
                    "REJECT",
                    width="stretch",
                    key="investigation_reject",
                ):
                    payload = {
                        "merchant_id": merchant_id,
                        "review_id": review_id,
                        "reviewer": reviewer,
                        "comments": comments,
                    }

                    try:
                        response = requests.post(
                            f"{API_URL}/review/{review_id}/reject",
                            json=payload,
                            timeout=30,
                        )

                        if response.status_code == 200:
                            st.session_state[
                                "review_result"
                            ] = response.json()

                            updated_case = get_case(
                                case.get("case_id")
                            )

                            if updated_case:
                                st.session_state["result"][
                                    "case"
                                ] = updated_case

                            st.rerun()

                        else:
                            st.error(response.text)

                    except Exception as exc:
                        st.error(
                            f"Rejection error: {exc}"
                        )

            with col3:
                if st.button(
                    "HOLD",
                    width="stretch",
                    key="investigation_hold",
                ):
                    payload = {
                        "merchant_id": merchant_id,
                        "review_id": review_id,
                        "reviewer": reviewer,
                        "comments": comments,
                    }

                    try:
                        response = requests.post(
                            f"{API_URL}/review/{review_id}/hold",
                            json=payload,
                            timeout=30,
                        )

                        if response.status_code == 200:
                            st.session_state[
                                "review_result"
                            ] = response.json()

                            updated_case = get_case(
                                case.get("case_id")
                            )

                            if updated_case:
                                st.session_state["result"][
                                    "case"
                                ] = updated_case

                            st.rerun()

                        else:
                            st.error(response.text)

                    except Exception as exc:
                        st.error(
                            f"Hold error: {exc}"
                        )

        # -------------------------------------------------
        # REVIEW RESULT
        # -------------------------------------------------

        if "review_result" in st.session_state:
            review_result = st.session_state[
                "review_result"
            ]

            st.divider()
            st.header("Human Review Result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Reviewer Decision",
                    review_result.get(
                        "review_decision",
                        "N/A",
                    ),
                )

            with col2:
                st.metric(
                    "Case Status",
                    review_result.get(
                        "case_status",
                        "N/A",
                    ),
                )

            with col3:
                st.metric(
                    "Review Status",
                    review_result.get(
                        "review_status",
                        "N/A",
                    ),
                )

            if review_result.get("status") == "APPROVED":
                st.success(
                    "Human review completed. The case has been approved."
                )
            elif review_result.get("status") == "REJECTED":
                st.error(
                    "Human review completed. The case has been rejected."
                )
            elif review_result.get("status") == "ON_HOLD":
                st.warning(
                    "Human review completed. The case is on hold."
                )
            else:
                st.info(
                    "Human review has been recorded."
                )

        # -------------------------------------------------
        # AUDIT TRAIL
        # -------------------------------------------------

        st.divider()
        st.header("Audit Trail")

        audit_merchant_id = str(
            result.get(
                "merchant_id",
                merchant_id,
            )
        ).strip().upper()

        audit_events = load_audit_events(
            audit_merchant_id
        )

        display_audit_events = filter_case_audit_events(
            audit_events,
            case,
        )

        if display_audit_events:
            case_id_text = (
                f" for case {case.get('case_id')}"
                if case and case.get("case_id")
                else ""
            )

            st.caption(
                f"{len(display_audit_events)} audit events recorded "
                f"for {audit_merchant_id}{case_id_text}."
            )

            # Display chronologically as a compact lifecycle.
            for event in reversed(display_audit_events):
                timestamp = event.get(
                    "timestamp",
                    "N/A",
                )

                event_type = str(
                    event.get(
                        "event_type",
                        "UNKNOWN",
                    )
                ).upper()

                details = event.get(
                    "details",
                    {},
                )

                if not isinstance(details, dict):
                    details = {}

                with st.expander(
                    f"{event_type}  •  {format_timestamp(timestamp)}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(
                            f"**Event:** {event_type}"
                        )
                        st.write(
                            f"**Merchant:** {audit_merchant_id}"
                        )

                    with col2:
                        if details.get("case_id"):
                            st.write(
                                f"**Case:** {details.get('case_id')}"
                            )

                        if details.get("review_id"):
                            st.write(
                                f"**Review:** {details.get('review_id')}"
                            )

                    st.json(details)

        else:
            st.info(
                "No audit events found for this investigation."
            )
