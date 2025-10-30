import socket
import ssl
import requests
from urllib.parse import urlparse

BLOCKLIST_FILE = 'blocklist.csv'  # simple local blocklist (one domain per line)

def in_local_blocklist(domain: str) -> bool:
    try:
        with open(BLOCKLIST_FILE) as f:
            lines = [l.strip().lower() for l in f if l.strip()]
        return domain.lower() in lines
    except FileNotFoundError:
        return False

def https_cert_valid(domain: str, timeout: int = 5) -> bool:
    """Attempt a simple TLS handshake to see if the domain serves HTTPS with a cert."""
    try:
        ctx = ssl.create_default_context()
        # Resolve hostname to an IP implicitly by socket.create_connection
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return bool(cert)
    except Exception:
        return False

def domain_is_safe(domain: str):
    """
    Returns (bool, meta)
    meta is a dict explaining the reason or details.
    """
    domain = domain.strip().lower()
    if not domain:
        return False, {'reason': 'empty-domain'}

    if in_local_blocklist(domain):
        return False, {'reason': 'local-blocklist'}

    ok = https_cert_valid(domain)
    if ok:
        return True, {'reason': 'https-ok'}
    return False, {'reason': 'no-https'}
