"""ASTRA Launcher Utilities — Port management and health checks."""

import argparse
import socket
import sys
import time
import urllib.request


def check_port(port: int) -> bool:
    """Return True if port is free, False if occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def free_ports(ports: list[int]) -> None:
    """Kill processes occupying the given ports (Windows)."""
    import subprocess
    for port in ports:
        try:
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                capture_output=True, text=True, shell=True
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 5 and "LISTENING" in line:
                    pid = parts[-1]
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True,
                                   capture_output=True)
        except Exception:
            pass


def wait_url(url: str, timeout: int = 30) -> bool:
    """Poll a URL until it responds 200 or timeout expires."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = urllib.request.urlopen(url, timeout=3)
            if resp.status == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    parser = argparse.ArgumentParser(description="ASTRA Launcher Utilities")
    parser.add_argument("--check-port", type=int, help="Check if a port is free")
    parser.add_argument("--free-ports", type=int, nargs="+", help="Kill processes on ports")
    parser.add_argument("--wait-url", nargs=2, metavar=("URL", "TIMEOUT"),
                        help="Wait for URL to respond")
    args = parser.parse_args()

    if args.check_port:
        sys.exit(0 if check_port(args.check_port) else 1)

    if args.free_ports:
        free_ports(args.free_ports)
        sys.exit(0)

    if args.wait_url:
        url, timeout = args.wait_url
        success = wait_url(url, int(timeout))
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
