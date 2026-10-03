"""ASTRA Launcher Banner — ASCII art banner for terminal display."""
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CYAN = "\033[96m"
WHITE = "\033[97m"
DIM = "\033[2m"
YELLOW = "\033[93m"
RESET = "\033[0m"

banner = f"""
{CYAN}    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║      █████╗ ███████╗████████╗██████╗  █████╗                 ║
    ║     ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗                ║
    ║     ███████║███████╗   ██║   ██████╔╝███████║                ║
    ║     ██╔══██║╚════██║   ██║   ██╔══██╗██╔══██║                ║
    ║     ██║  ██║███████║   ██║   ██║  ██║██║  ██║                ║
    ║     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝                ║
    ║                                                              ║
    ║  {WHITE}Algorithm Security Tracking & Risk Assessment{CYAN}              ║
    ║  {DIM}SIH26164 ECDAT  |  Post-Quantum Migration Engine{CYAN}{RESET}{CYAN}         ║
    ║  {DIM}NIST FIPS 203 (ML-KEM) | 204 (ML-DSA) | 205 (SLH-DSA){CYAN}{RESET}{CYAN}   ║
    ║                                                              ║
    ║  {YELLOW}Built by HEXARK{CYAN}                                             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝{RESET}
"""

try:
    print(banner)
except Exception:
    print("\n    [+] ASTRA — Algorithm Security Tracking and Risk Assessment (SIH26164 ECDAT)")
    print("    [+] NIST FIPS 203 | 204 | 205 — Built by HEXARK\n")
