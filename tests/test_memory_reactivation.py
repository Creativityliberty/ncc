from ncc.metrics import delayed_intent_reactivation


def test_delayed_intent_reactivation_ok():
    required = ["target_os=mac", "local_first"]
    current = ["target_os=mac", "local_first", "include_tests"]

    assert delayed_intent_reactivation(required, current) == 1.0


def test_delayed_intent_reactivation_partial():
    required = ["target_os=mac", "local_first"]
    current = ["target_os=mac"]

    assert delayed_intent_reactivation(required, current) == 0.5


def test_delayed_intent_reactivation_empty_required():
    assert delayed_intent_reactivation([], ["anything"]) == 1.0
