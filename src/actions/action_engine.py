import os
import json
from datetime import datetime


# ==========================================================
# REVENUEOS-AI ACTION ENGINE
# ==========================================================

ACTION_LOG_FILE = "data/processed/action_log.json"


# ==========================================================
# ACTION DEFINITIONS
# ==========================================================

ACTION_DEFINITIONS = {

    "NO_ACTION": {
        "action_type": "NO_ACTION",
        "priority": "LOW",
        "human_approval_required": False,
        "description": (
            "No operational action is required. "
            "Merchant remains within acceptable risk limits."
        )
    },

    "MONITOR": {
        "action_type": "MONITOR_MERCHANT",
        "priority": "MEDIUM",
        "human_approval_required": False,
        "description": (
            "Merchant should be monitored for continued "
            "risk or transaction failure behaviour."
        )
    },

    "INVESTIGATE": {
        "action_type": "START_INVESTIGATION",
        "priority": "HIGH",
        "human_approval_required": False,
        "description": (
            "Automated investigation should be performed "
            "to identify the likely cause of merchant risk."
        )
    },

    "ESCALATE": {
        "action_type": "HUMAN_REVIEW",
        "priority": "CRITICAL",
        "human_approval_required": True,
        "description": (
            "Critical merchant risk requires immediate "
            "human review and intervention."
        )
    }
}


# ==========================================================
# EXECUTE ACTION
# ==========================================================

def execute_action(decision_result):

    """
    Convert the decision agent output into
    an operational action.
    """

    # ------------------------------------------------------
    # VALIDATE INPUT
    # ------------------------------------------------------

    if decision_result is None:

        return {
            "status": "ERROR",
            "message": "Decision result is None."
        }

    if not isinstance(decision_result, dict):

        return {
            "status": "ERROR",
            "message": "Decision result must be a dictionary."
        }

    # ------------------------------------------------------
    # EXTRACT DATA
    # ------------------------------------------------------

    merchant_id = decision_result.get(
        "merchant_id",
        "UNKNOWN"
    )

    decision = str(
        decision_result.get(
            "decision",
            "UNKNOWN"
        )
    ).strip().upper()

    risk_score = decision_result.get(
        "risk_score",
        None
    )

    risk_category = decision_result.get(
        "risk_category",
        "UNKNOWN"
    )

    failure_rate = decision_result.get(
        "failure_rate",
        None
    )

    reason = decision_result.get(
        "reason",
        ""
    )

    # ------------------------------------------------------
    # VALIDATE DECISION
    # ------------------------------------------------------

    if decision not in ACTION_DEFINITIONS:

        return {
            "status": "ERROR",
            "merchant_id": merchant_id,
            "decision": decision,
            "message": (
                f"Unsupported decision: {decision}"
            )
        }

    action_definition = ACTION_DEFINITIONS[
        decision
    ]

    # ------------------------------------------------------
    # CREATE ACTION
    # ------------------------------------------------------

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    action_result = {

        "status": "ACTION_CREATED",

        "timestamp": timestamp,

        "merchant_id": merchant_id,

        "risk_score": risk_score,

        "risk_category": risk_category,

        "failure_rate": failure_rate,

        "decision": decision,

        "action_type":
            action_definition["action_type"],

        "priority":
            action_definition["priority"],

        "human_approval_required":
            action_definition[
                "human_approval_required"
            ],

        "action_description":
            action_definition[
                "description"
            ],

        "decision_reason":
            reason
    }

    # ------------------------------------------------------
    # ATTACH INVESTIGATION
    # ------------------------------------------------------

    investigation = decision_result.get(
        "investigation"
    )

    if investigation is not None:

        action_result[
            "investigation_available"
        ] = True

        action_result[
            "investigation"
        ] = investigation

    else:

        action_result[
            "investigation_available"
        ] = False

    # ------------------------------------------------------
    # DETERMINE NEXT STEP
    # ------------------------------------------------------

    if decision == "ESCALATE":

        action_result[
            "next_step"
        ] = (
            "Human approval required before "
            "executing the recommended action."
        )

    elif decision == "INVESTIGATE":

        action_result[
            "next_step"
        ] = (
            "Proceed with automated merchant "
            "risk investigation."
        )

    elif decision == "MONITOR":

        action_result[
            "next_step"
        ] = (
            "Add merchant to monitoring queue "
            "and continue observing risk metrics."
        )

    elif decision == "NO_ACTION":

        action_result[
            "next_step"
        ] = (
            "No further operational action required."
        )

    # ------------------------------------------------------
    # SAVE ACTION
    # ------------------------------------------------------

    save_action(action_result)

    return action_result


# ==========================================================
# SAVE ACTION TO JSON
# ==========================================================

def save_action(action_result):

    try:

        directory = os.path.dirname(
            ACTION_LOG_FILE
        )

        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )

        # --------------------------------------------------
        # LOAD EXISTING ACTIONS
        # --------------------------------------------------

        if os.path.exists(
            ACTION_LOG_FILE
        ):

            try:

                with open(
                    ACTION_LOG_FILE,
                    "r",
                    encoding="utf-8"
                ) as file:

                    actions = json.load(file)

            except (
                json.JSONDecodeError,
                FileNotFoundError
            ):

                actions = []

        else:

            actions = []

        if not isinstance(
            actions,
            list
        ):

            actions = []

        # --------------------------------------------------
        # APPEND ACTION
        # --------------------------------------------------

        actions.append(
            action_result
        )

        # --------------------------------------------------
        # SAVE
        # --------------------------------------------------

        with open(
            ACTION_LOG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                actions,
                file,
                indent=4,
                default=str
            )

        return True

    except Exception as e:

        print(
            "\nWARNING: Could not save action log."
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        return False


# ==========================================================
# DISPLAY ACTION
# ==========================================================

def display_action(action):

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI ACTION ENGINE")
    print("=" * 70)

    # ------------------------------------------------------
    # ERROR
    # ------------------------------------------------------

    if action.get("status") == "ERROR":

        print("\nSTATUS:")
        print("ERROR")

        print(
            f"\nMessage: "
            f"{action.get('message')}"
        )

        print("=" * 70)

        return

    # ------------------------------------------------------
    # ACTION ASSESSMENT
    # ------------------------------------------------------

    print("\nACTION ASSESSMENT")
    print("-" * 70)

    print(
        f"Merchant ID:              "
        f"{action.get('merchant_id')}"
    )

    print(
        f"Risk Score:               "
        f"{action.get('risk_score')}"
    )

    print(
        f"Risk Category:            "
        f"{action.get('risk_category')}"
    )

    print(
        f"Failure Rate:             "
        f"{action.get('failure_rate')}"
    )

    print(
        f"Decision:                 "
        f"{action.get('decision')}"
    )

    # ------------------------------------------------------
    # OPERATIONAL ACTION
    # ------------------------------------------------------

    print("\n")
    print("OPERATIONAL ACTION")
    print("-" * 70)

    print(
        f"Action Type:              "
        f"{action.get('action_type')}"
    )

    print(
        f"Priority:                 "
        f"{action.get('priority')}"
    )

    print(
        f"Human Approval Required:  "
        f"{action.get('human_approval_required')}"
    )

    print(
        f"\nAction Description:\n"
        f"{action.get('action_description')}"
    )

    print(
        f"\nNext Step:\n"
        f"{action.get('next_step')}"
    )

    print(
        f"\nDecision Reason:\n"
        f"{action.get('decision_reason')}"
    )

    # ------------------------------------------------------
    # INVESTIGATION
    # ------------------------------------------------------

    if action.get(
        "investigation_available",
        False
    ):

        print("\n")
        print("INVESTIGATION AVAILABLE")
        print("-" * 70)

        investigation = action.get(
            "investigation"
        )

        print(
            json.dumps(
                investigation,
                indent=4,
                default=str
            )
        )

    # ------------------------------------------------------
    # LOG
    # ------------------------------------------------------

    print("\n")
    print(
        f"Action Log: {ACTION_LOG_FILE}"
    )

    print("=" * 70)
    print("ACTION ENGINE COMPLETE")
    print("=" * 70)


# ==========================================================
# TEST DECISION
# ==========================================================

def create_test_decision():

    return {

        "merchant_id": "M00005",

        "risk_score": 100.00,

        "risk_category": "Critical",

        "failure_rate": 0.1150,

        "decision": "INVESTIGATE",

        "reason": (
            "Very high merchant risk detected. "
            "Automated investigation is required."
        )
    }


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI ACTION ENGINE TEST")
    print("=" * 70)

    # ------------------------------------------------------
    # CREATE TEST DECISION
    # ------------------------------------------------------

    decision_result = create_test_decision()

    print("\nINPUT DECISION")
    print("-" * 70)

    print(
        json.dumps(
            decision_result,
            indent=4
        )
    )

    # ------------------------------------------------------
    # EXECUTE ACTION
    # ------------------------------------------------------

    try:

        action = execute_action(
            decision_result
        )

        # --------------------------------------------------
        # DISPLAY RESULT
        # --------------------------------------------------

        display_action(
            action
        )

    except Exception as e:

        print("\n")
        print("-" * 70)
        print("ACTION ENGINE ERROR")
        print("-" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )

        raise