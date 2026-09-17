from facilito.models import UnitOutcome


def test_unit_outcome_defaults():
    outcome = UnitOutcome(success=True)

    assert outcome.success is True
    assert outcome.error is None
    assert outcome.provider == "hls"


def test_unit_outcome_failure():
    outcome = UnitOutcome(success=False, error="HTTP 429", provider="youtube")

    assert outcome.success is False
    assert outcome.error == "HTTP 429"
    assert outcome.provider == "youtube"
