"""ASTRA Launcher Banner — ASCII art banner for terminal display."""

CYAN = "\033[96m"
WHITE = "\033[97m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"

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
    ║  {WHITE}Enterprise Cryptographic Discovery & Analysis Tool{CYAN}         ║
    ║  {DIM}SIH26164 ECDAT  |  Post-Quantum Migration Engine{CYAN}{RESET}{CYAN}         ║
    ║  {DIM}NIST FIPS 203 (ML-KEM) | 204 (ML-DSA) | 205 (SLH-DSA){CYAN}{RESET}{CYAN}   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝{RESET}
"""

print(banner)
