class InvestigationState:

    def __init__(
        self,
        merchant_id,
        risk_score,
        risk_category,
        failure_rate
    ):

        self.merchant_id = merchant_id

        self.risk_score = risk_score

        self.risk_category = risk_category

        self.failure_rate = failure_rate

        # Tools already executed
        self.tools_used = []

        # Evidence collected from tools
        self.evidence = {}

        # Current investigation status
        self.status = "STARTED"

        # Final conclusion
        self.conclusion = None

        # Recommended action
        self.recommendation = None

        self.confidence = None

    def add_evidence(
        self,
        tool_name,
        result
    ):

        self.tools_used.append(
            tool_name
        )

        self.evidence[
            tool_name
        ] = result

    def get_state(self):

        return {
            "merchant_id":
                self.merchant_id,

            "risk_score":
                self.risk_score,

            "risk_category":
                self.risk_category,

            "failure_rate":
                self.failure_rate,

            "tools_used":
                self.tools_used,

            "evidence":
                self.evidence,

            "status":
                self.status,

            "conclusion":
                self.conclusion,

            "recommendation":
                self.recommendation,

            "confidence":
                 self.confidence,
        }