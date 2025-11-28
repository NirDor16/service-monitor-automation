from monitor.network_checker import check_network, check_all_network


def test_network_returns_boolean():
    """
    Check that the main network check function returns a boolean.
    """
    result = check_network()
    assert isinstance(result, bool)


def test_individual_checks_have_required_fields():
    """
    Ensure each network check returns the expected structure.
    """
    results = check_all_network()

    for r in results:
        assert "ok" in r
        assert "response_time_ms" in r
        assert "type" in r
