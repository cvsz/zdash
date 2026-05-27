from .models import Capability


def default_capability_map() -> list[Capability]:
    return [
        Capability(name="Governance", maturity=3, owner="CISO"),
        Capability(name="Delivery", maturity=3, owner="CTO"),
    ]
