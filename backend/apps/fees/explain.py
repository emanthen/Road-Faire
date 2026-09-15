from decimal import Decimal


def explain_recommendation(
    cheaper: str, pay_as_you_go_total: Decimal, annual_pass_total: Decimal, savings: Decimal
) -> str:
    if cheaper == "tie":
        return (
            f"Paying as you go and buying the annual pass both come to "
            f"${pay_as_you_go_total:.2f} — either works, it's your call."
        )
    if cheaper == "annual_pass":
        return (
            f"The annual pass is cheaper here: ${annual_pass_total:.2f} versus "
            f"${pay_as_you_go_total:.2f} paying as you go. You'll save ${savings:.2f}."
        )
    return (
        f"Paying as you go is cheaper here: ${pay_as_you_go_total:.2f} versus "
        f"${annual_pass_total:.2f} for the annual pass. You'll save ${savings:.2f}."
    )
