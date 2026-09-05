import json
import os
from datetime import datetime


CASE_FILE = (
    "data/processed/investigation_cases.json"
)


# ==========================================================
# CONFIGURATION
# ==========================================================

ACTIVE_CASE_STATUSES = {
    "OPEN",
    "PENDING_HUMAN_REVIEW",
    "ON_HOLD"
}


# ==========================================================
# INTERNAL: LOAD CASES
# ==========================================================

def _load_cases():

    if not os.path.exists(CASE_FILE):
        return []

    try:

        with open(
            CASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ==========================================================
# INTERNAL: SAVE CASES
# ==========================================================

def _save_cases(cases):

    directory = os.path.dirname(CASE_FILE)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        CASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cases,
            file,
            indent=4,
            default=str
        )


# ==========================================================
# GET ACTIVE CASE FOR MERCHANT
# ==========================================================

def get_active_case_for_merchant(
    merchant_id
):

    cases = _load_cases()

    merchant_cases = [

        case
        for case in cases

        if (
            str(case.get("merchant_id"))
            == str(merchant_id)
            and
            case.get("status")
            in ACTIVE_CASE_STATUSES
        )

    ]

    if not merchant_cases:
        return None

    # Return the most recently updated active case.

    merchant_cases.sort(
        key=lambda case:
            case.get(
                "updated_at",
                case.get(
                    "created_at",
                    ""
                )
            )
    )

    return merchant_cases[-1]


# ==========================================================
# CREATE CASE
# ==========================================================

def create_case(
    merchant_id,
    risk_score,
    risk_category,
    findings,
    recommended_action,
    confidence
):

    # ------------------------------------------------------
    # Load existing cases
    # ------------------------------------------------------

    cases = _load_cases()


    # ------------------------------------------------------
    # Generate next case number
    # ------------------------------------------------------

    case_numbers = []

    for case in cases:

        case_id = str(
            case.get(
                "case_id",
                ""
            )
        )

        prefix = (
            f"CASE-{merchant_id}-"
        )

        if case_id.startswith(prefix):

            try:

                number = int(
                    case_id.replace(
                        prefix,
                        ""
                    )
                )

                case_numbers.append(
                    number
                )

            except ValueError:

                continue


    if case_numbers:

        next_number = max(
            case_numbers
        ) + 1

    else:

        next_number = 1


    case_id = (
        f"CASE-{merchant_id}-"
        f"{next_number:05d}"
    )


    # ------------------------------------------------------
    # Create case
    # ------------------------------------------------------

    now = datetime.now().isoformat()

    case = {

        "case_id":
            case_id,

        "merchant_id":
            merchant_id,

        "risk_score":
            risk_score,

        "risk_category":
            risk_category,

        "findings":
            findings,

        "recommended_action":
            recommended_action,

        "confidence":
            confidence,

        "status":
            "OPEN",

        "review_id":
            None,

        "review_status":
            "NOT_REQUIRED",

        "reviewer":
            None,

        "review_decision":
            None,

        "review_comments":
            None,

        "created_at":
            now,

        "updated_at":
            now
    }


    cases.append(case)

    _save_cases(cases)

    return case


# ==========================================================
# GET CASE BY ID
# ==========================================================

def get_case(case_id):

    cases = _load_cases()

    for case in cases:

        if case.get(
            "case_id"
        ) == case_id:

            return case

    return None


# ==========================================================
# GET LATEST CASE BY MERCHANT
# ==========================================================

def get_latest_case_for_merchant(
    merchant_id
):

    cases = _load_cases()

    merchant_cases = [

        case
        for case in cases

        if str(
            case.get("merchant_id")
        ) == str(merchant_id)

    ]

    if not merchant_cases:
        return None

    merchant_cases.sort(
        key=lambda case:
            case.get(
                "updated_at",
                case.get(
                    "created_at",
                    ""
                )
            )
    )

    return merchant_cases[-1]


# ==========================================================
# UPDATE CASE
# ==========================================================

def update_case(
    case_id,
    updates
):

    cases = _load_cases()

    for index, case in enumerate(cases):

        if case.get(
            "case_id"
        ) != case_id:

            continue

        case.update(
            updates
        )

        case["updated_at"] = (
            datetime.now().isoformat()
        )

        cases[index] = case

        _save_cases(cases)

        return case

    return None


# ==========================================================
# UPDATE CASE STATUS
# ==========================================================

def update_case_status(
    case_id,
    status
):

    return update_case(
        case_id,
        {
            "status":
                status
        }
    )


# ==========================================================
# LINK REVIEW TO CASE
# ==========================================================

def link_review_to_case(
    case_id,
    review_id
):

    return update_case(
        case_id,
        {
            "review_id":
                review_id,

            "review_status":
                "PENDING",

            "status":
                "PENDING_HUMAN_REVIEW"
        }
    )


# ==========================================================
# COMPLETE CASE REVIEW
# ==========================================================

def complete_case_review(
    case_id,
    review_decision,
    reviewer,
    comments=None
):

    decision = str(
        review_decision
    ).upper().strip()


    if decision == "APPROVE":

        status = "APPROVED"

    elif decision == "REJECT":

        status = "REJECTED"

    elif decision == "HOLD":

        status = "ON_HOLD"

    else:

        raise ValueError(
            "Review decision must be "
            "APPROVE, REJECT, or HOLD."
        )


    return update_case(
        case_id,
        {
            "status":
                status,

            "review_status":
                status,

            "reviewer":
                reviewer,

            "review_decision":
                decision,

            "review_comments":
                comments
        }
    )


# ==========================================================
# GET ALL CASES
# ==========================================================

def get_all_cases():

    return _load_cases()


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("REVENUEOS-AI CASE MANAGER")
    print("=" * 70)


    print("\nChecking active case...")

    active_case = get_active_case_for_merchant(
        "M00005"
    )


    if active_case:

        print("\nACTIVE CASE FOUND")

        print(
            f"Case ID: "
            f"{active_case['case_id']}"
        )

        print(
            f"Status: "
            f"{active_case['status']}"
        )

    else:

        print(
            "\nNo active case found."
        )


    print("\nTesting unique case creation...")

    case_1 = create_case(
        merchant_id="M00008",
        risk_score=30.12,
        risk_category="Medium",
        findings=[
            "Elevated transaction failure rate"
        ],
        recommended_action="MONITOR",
        confidence=0.80
    )

    case_2 = create_case(
        merchant_id="M00008",
        risk_score=30.12,
        risk_category="Medium",
        findings=[
            "Second investigation event"
        ],
        recommended_action="MONITOR",
        confidence=0.80
    )

    print(
        f"\nFirst Case ID:  "
        f"{case_1['case_id']}"
    )

    print(
        f"Second Case ID: "
        f"{case_2['case_id']}"
    )

    if case_1["case_id"] != case_2["case_id"]:

        print(
            "\n✓ Unique case creation working"
        )

    else:

        print(
            "\n✗ Unique case creation failed"
        )


    print("\n")
    print("=" * 70)
    print("CASE MANAGER TEST COMPLETE")
    print("=" * 70)