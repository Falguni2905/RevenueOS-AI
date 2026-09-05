import streamlit as st
import requests


# ==========================================================
# CONFIGURATION
# ==========================================================

API_URL = "http://127.0.0.1:8000"


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="RevenueOS-AI",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# HEADER
# ==========================================================

st.title("REVENUEOS-AI")
st.subheader("Autonomous Merchant Risk Investigation")

st.markdown(
    """
    Enter a merchant ID to assess its risk, decision status,
    investigation findings, and recommended action.
    """
)

st.divider()


# ==========================================================
# MERCHANT INPUT
# ==========================================================

merchant_id = st.text_input(
    "Merchant ID",
    value="M00005",
    placeholder="Example: M00005"
)


# ==========================================================
# RUN ANALYSIS
# ==========================================================

if st.button(
    "Run Merchant Investigation",
    type="primary"
):

    if not merchant_id.strip():

        st.warning(
            "Please enter a merchant ID."
        )

    else:

        merchant_id = merchant_id.strip().upper()

        try:

            with st.spinner(
                "Analyzing merchant..."
            ):

                response = requests.get(
                    f"{API_URL}/merchant/{merchant_id}",
                    timeout=30
                )

            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------

            if response.status_code == 200:

                data = response.json()

                st.success(
                    "Merchant analysis completed."
                )

                # ==================================================
                # RISK ASSESSMENT
                # ==================================================

                st.header("Risk Assessment")

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Merchant ID",
                        data.get(
                            "merchant_id",
                            merchant_id
                        )
                    )

                with col2:

                    st.metric(
                        "Risk Score",
                        f"{float(data.get('risk_score', 0)):.2f}"
                    )

                with col3:

                    st.metric(
                        "Risk Category",
                        data.get(
                            "risk_category",
                            "N/A"
                        )
                    )

                with col4:

                    failure_rate = float(
                        data.get(
                            "failure_rate",
                            0
                        )
                    )

                    # Handles decimal representation
                    # such as 0.0769 = 7.69%

                    if failure_rate <= 1:

                        failure_display = (
                            f"{failure_rate * 100:.2f}%"
                        )

                    else:

                        failure_display = (
                            f"{failure_rate:.2f}%"
                        )

                    st.metric(
                        "Failure Rate",
                        failure_display
                    )

                # ==================================================
                # DECISION
                # ==================================================

                st.divider()

                st.header("Decision")

                decision = data.get(
                    "decision",
                    "UNKNOWN"
                )

                reason = data.get(
                    "reason",
                    "No reason provided."
                )

                if decision == "ESCALATE":

                    st.error(
                        f"Decision: {decision}"
                    )

                elif decision == "INVESTIGATE":

                    st.warning(
                        f"Decision: {decision}"
                    )

                elif decision == "MONITOR":

                    st.info(
                        f"Decision: {decision}"
                    )

                elif decision == "NO_ACTION":

                    st.success(
                        f"Decision: {decision}"
                    )

                else:

                    st.warning(
                        f"Decision: {decision}"
                    )

                st.write(
                    f"**Reason:** {reason}"
                )

                # ==================================================
                # ACTION PLAN
                # ==================================================

                action_plan = data.get(
                    "action_plan"
                )

                if action_plan:

                    st.divider()

                    st.header("Action Plan")

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Action",
                            action_plan.get(
                                "action",
                                "N/A"
                            )
                        )

                    with col2:

                        st.metric(
                            "Priority",
                            action_plan.get(
                                "priority",
                                "N/A"
                            )
                        )

                    with col3:

                        st.metric(
                            "Status",
                            action_plan.get(
                                "status",
                                "N/A"
                            )
                        )

                    st.write(
                        "**Description:** "
                        + str(
                            action_plan.get(
                                "description",
                                "N/A"
                            )
                        )
                    )

                    st.write(
                        "**Next Step:** "
                        + str(
                            action_plan.get(
                                "next_step",
                                "N/A"
                            )
                        )
                    )

                    st.write(
                        "**Human Approval Required:** "
                        + str(
                            action_plan.get(
                                "human_approval_required",
                                "N/A"
                            )
                        )
                    )

                # ==================================================
                # AUTOMATED INVESTIGATION
                # ==================================================

                investigation = data.get(
                    "investigation"
                )

                if investigation:

                    st.divider()

                    st.header(
                        "Automated Investigation"
                    )

                    analysis = investigation.get(
                        "root_cause_analysis",
                        {}
                    )

                    recommendation = investigation.get(
                        "recommendation",
                        {}
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            "**Dominant Failure**"
                        )

                        st.info(
                            str(
                                analysis.get(
                                    "dominant_failure_reason",
                                    "N/A"
                                )
                            )
                        )

                    with col2:

                        st.write(
                            "**Likely Cause**"
                        )

                        st.info(
                            str(
                                analysis.get(
                                    "likely_cause",
                                    "N/A"
                                )
                            )
                        )

                    st.subheader(
                        "Recommended Action"
                    )

                    st.write(
                        recommendation.get(
                            "action",
                            "N/A"
                        )
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Confidence",
                            str(
                                recommendation.get(
                                    "confidence",
                                    "N/A"
                                )
                            )
                        )

                    with col2:

                        st.metric(
                            "Human Approval",
                            str(
                                recommendation.get(
                                    "human_approval_required",
                                    "N/A"
                                )
                            )
                        )

                else:

                    # --------------------------------------------------
                    # No investigation required
                    # --------------------------------------------------

                    st.divider()

                    st.header(
                        "Automated Investigation"
                    )

                    st.info(
                        "No automated investigation was triggered "
                        "for this merchant because the current "
                        "decision does not require investigation."
                    )

            # ======================================================
            # API ERROR
            # ======================================================

            else:

                st.error(
                    f"API returned HTTP {response.status_code}"
                )

                try:

                    error_data = response.json()

                    st.json(
                        error_data
                    )

                except Exception:

                    st.write(
                        response.text
                    )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the RevenueOS-AI API."
            )

            st.write(
                "Make sure FastAPI is running on:"
            )

            st.code(
                "http://127.0.0.1:8000"
            )

        except requests.exceptions.Timeout:

            st.error(
                "The API request timed out."
            )

        except Exception as e:

            st.error(
                f"Unexpected error: {type(e).__name__}: {e}"
            )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "RevenueOS-AI | Autonomous Merchant Risk Investigation"
)