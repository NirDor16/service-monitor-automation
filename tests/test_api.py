from monitor.api_checker import check_all_services

def test_api_services_format():
    results = check_all_services()
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    for r in results:
        assert "name" in r
        assert "url" in r
        assert "ok" in r
        assert "status_code" in r
        assert "response_time_ms" in r
