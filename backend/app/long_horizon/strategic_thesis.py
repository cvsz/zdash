from .models import StrategicThesis


def thesis_tracker() -> list[StrategicThesis]:
    return [
        StrategicThesis(
            thesis="Trust-first automation compounds enterprise adoption",
            confidence=0.68,
            horizon_years=5,
        )
    ]
