import platform
import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

import yaml
from .logger import logger
from .alert import send_alert

# Path to shared configuration file
CONFIG_PATH = Path(__file__).with_name("config.yaml")


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """
    Load YAML configuration and return it as a Python dict.
    """
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data or {}


# ---------- Low-level network check functions ----------

def ping_host(host: str, count: int = 3, timeout: float = 2.0) -> Dict[str, Any]:
    """
    Execute a system ping command.
    Uses different flags for Windows vs Linux/macOS.
    Returns a dict containing success status, response time, and error if any.
    """
    system = platform.system().lower()

    if system.startswith("win"):
        cmd = ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]

    start = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    duration_ms = (time.perf_counter() - start) * 1000

    ok = proc.returncode == 0

    return {
        "type": "ping",
        "host": host,
        "ok": ok,
        "response_time_ms": round(duration_ms, 2),
        "error": None if ok else proc.stderr.strip() or proc.stdout.strip(),
    }


def dns_lookup(host: str) -> Dict[str, Any]:
    """
    Resolve a DNS hostname into an IP address.
    """
    start = time.perf_counter()

    try:
        ip = socket.gethostbyname(host)
        duration_ms = (time.perf_counter() - start) * 1000

        return {
            "type": "dns",
            "host": host,
            "ok": True,
            "ip": ip,
            "response_time_ms": round(duration_ms, 2),
            "error": None,
        }
    except socket.gaierror as exc:
        duration_ms = (time.perf_counter() - start) * 1000

        return {
            "type": "dns",
            "host": host,
            "ok": False,
            "ip": None,
            "response_time_ms": round(duration_ms, 2),
            "error": str(exc),
        }


def tcp_connect(host: str, port: int, timeout: float = 3.0) -> Dict[str, Any]:
    """
    Attempt to open a TCP connection to host:port within a given timeout.
    """
    start = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((host, port))
        duration_ms = (time.perf_counter() - start) * 1000
        ok = (result == 0)
        error = None
    except OSError as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        ok = False
        error = str(exc)
    finally:
        sock.close()

    return {
        "type": "tcp",
        "host": host,
        "port": port,
        "ok": ok,
        "response_time_ms": round(duration_ms, 2),
        "error": error,
    }


# ---------- High-level config-driven logic ----------

def check_network_item(conf: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine which kind of network check to run based on config definition.
    """
    check_type = conf.get("type", "ping")
    name = conf.get("name", f"{check_type} {conf.get('host', '')}")
    host = conf["host"]

    if check_type == "ping":
        result = ping_host(
            host,
            count=int(conf.get("count", 3)),
            timeout=float(conf.get("timeout", 2.0)),
        )
    elif check_type == "dns":
        result = dns_lookup(host)
    elif check_type == "tcp":
        result = tcp_connect(
            host,
            port=int(conf["port"]),
            timeout=float(conf.get("timeout", 3.0)),
        )
    else:
        # Unknown check type → mark as failure
        result = {
            "type": check_type,
            "host": host,
            "ok": False,
            "response_time_ms": 0.0,
            "error": f"Unknown check type: {check_type}",
        }

    result["name"] = name
    return result


def check_all_network() -> List[Dict[str, Any]]:
    """
    Run all network checks defined in the configuration file.
    """
    config = load_config()
    checks = config.get("network_checks", [])
    return [check_network_item(conf) for conf in checks]


def check_network() -> bool:
    """
    Utility method used by tests.
    Returns True if all network checks passed.
    """
    results = check_all_network()
    return all(r.get("ok", False) for r in results)


def print_results_table(results: List[Dict[str, Any]]) -> None:
    """
    Print a formatted results table for all network checks.
    """
    print("\nNETWORK CHECK RESULTS")
    print("-" * 70)

    for r in results:
        name = r.get("name", "")
        check_type = r.get("type", "")
        status = "OK" if r.get("ok") else "FAIL"
        time_ms = f'{r.get("response_time_ms", 0)} ms'
        extra = ""

        if check_type == "dns" and r.get("ip"):
            extra = r["ip"]
        elif check_type == "tcp" and r.get("port"):
            extra = f"port {r['port']}"

        print(f"{name:20} | {check_type:4} | {status:6} | {time_ms:10} | {extra}")

    print("-" * 70)


def main() -> None:
    results = check_all_network()
    print_results_table(results)

    # Log all network checks
    for r in results:
        name = r.get("name", "Unknown")
        check_type = r.get("type", "")
        t = r.get("response_time_ms")

        if r.get("ok"):
            logger.info("NET OK: %s [%s] time=%sms", name, check_type, t)
        else:
            logger.error(
                "NET FAIL: %s [%s] time=%sms error=%s",
                name, check_type, t, r.get("error"),
            )

    # Send alert if failures were detected
    failed = [r for r in results if not r.get("ok", False)]

    if failed:
        lines = ["Network check failures detected:"]
        for r in failed:
            name = r.get("name", "Unknown")
            check_type = r.get("type", "")
            extra = r.get("error") or ""
            lines.append(f"- {name} [{check_type}] {extra}")

        send_alert("\n".join(lines))
    else:
        logger.info("All network checks passed")


if __name__ == "__main__":
    main()
