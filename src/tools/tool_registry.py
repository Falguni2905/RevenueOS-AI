from src.tools.merchant_tools import (
    merchant_profile,
    failure_analysis,
    payment_method_analysis,
    hourly_analysis,
    transaction_analysis
)


TOOL_REGISTRY = {

    "merchant_profile": {
        "function": merchant_profile,
        "description": (
            "Get merchant characteristics, "
            "size, category, geography, "
            "payment configuration and "
            "baseline performance."
        )
    },

    "failure_analysis": {
        "function": failure_analysis,
        "description": (
            "Analyze payment failures and "
            "identify dominant failure reasons."
        )
    },

    "payment_method_analysis": {
        "function": payment_method_analysis,
        "description": (
            "Compare failure rates across "
            "payment methods."
        )
    },

    "hourly_analysis": {
        "function": hourly_analysis,
        "description": (
            "Identify time-of-day patterns "
            "in transaction failures."
        )
    },

    "transaction_analysis": {
        "function": transaction_analysis,
        "description": (
            "Inspect the highest-value "
            "transactions for the merchant."
        )
    }
}


def list_tools():

    return {
        name: tool["description"]
        for name, tool in TOOL_REGISTRY.items()
    }


def execute_tool(
    tool_name,
    merchant_id
):

    if tool_name not in TOOL_REGISTRY:

        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }

    tool = TOOL_REGISTRY[
        tool_name
    ]

    return tool["function"](
        merchant_id
    )