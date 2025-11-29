import time
from pathlib import Path
from typing import List, Dict, Any

import requests
import yaml
from .alert import send_alert
from .logger import logger
from .config_loader import load_config


def check_service(service_conf: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a single API check based on service configuration.
    Returns a dictionary containing the check results.
    """
    url = service_conf["url"]
    expected_status = service_conf.get("expected_status", 200)
    timeout = float(service_conf.get("timeout", 5))
    name = service_conf.get("name", url)

    start = time.perf_counter()

    try:
        response = requests.get(url, timeout=timeout)
        duration_ms = (time.perf_counter() - start) * 1000

        ok = response.status_code == expected_status

        return {
            "name": name,
            "url": url,
            "ok": ok,
            "status_code": response.status_code,
            "response_time_ms": round(duration_ms, 2),
            "error": None,
        }

    except requests.RequestException as exc:
        duration_ms = (time.perf_counter() - start) * 1000

        return {
            "name": name,
            "url": url,
            "ok": False,
            "status_code": None,
            "response_time_ms": round(duration_ms, 2),
            "error": str(exc),
        }


def check_all_services() -> List[Dict[str, Any]]:
    """
    Load configuration and run checks for all services.
    Returns a list of result dictionaries.
    """
    config = load_config()
    services = config.get("services", [])

    results: List[Dict[str, Any]] = []

    for service in services:
        result = check_service(service)
        results.append(result)

    return results


def print_results_table(results):
    """
    Print a formatted summary table of all service check results.
    """
    print("\nSERVICE CHECK RESULTS")
    print("-" * 60)

    for r in results:
        name = r["name"]
        status = "OK" if r["ok"] else "FAIL"
        code = r["status_code"] if r["status_code"] is not None else "ERR"
        time_ms = f'{r["response_time_ms"]} ms'

        print(f"{name:20} | {status:6} | {code:4} | {time_ms}")

    print("-" * 60)


def main() -> None:
    """
    Main execution workflow:
    - Run all service checks
    - Print results table
    - Write logs
    - Trigger Slack alerts on failures
    """
    results = check_all_services()
    print_results_table(results)

    # Log all service results
    for r in results:
        name = r.get("name", "Unknown")
        code = r.get("status_code")
        t = r.get("response_time_ms")

        if r.get("ok"):
            logger.info("API OK: %s status=%s time=%sms", name, code, t)
        else:
            logger.error("API FAIL: %s status=%s time=%sms", name, code, t)

    # Send alert if any service failed
    failed = [r for r in results if not r.get("ok", False)]
    if failed:
        lines = ["API check failures detected:"]
        for r in failed:
            name = r.get("name", "Unknown")
            status = r.get("status_code")
            lines.append(f"- {name} (status={status})")

        send_alert("\n".join(lines))
    else:
        logger.info("All API checks passed")


if __name__ == "__main__":
    main()
