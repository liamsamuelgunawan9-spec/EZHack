# ============================================================
# Blocks/__init__.py
# Assembles structure, recon, and attack block modules into
# the three combined strings that Main.py needs:
#   TOOLBOX_XML, BLOCK_DEFINITIONS_JS, PYTHON_GENERATORS_JS
# and the unified run_scan() dispatcher.
# ============================================================

from Blocks import structure_blocks, recon_blocks, attack_blocks

# ── Combined Toolbox XML ─────────────────────────────────────
TOOLBOX_XML = f"""
<xml id="toolbox" style="display: none">
  {structure_blocks.TOOLBOX_XML}
  {recon_blocks.TOOLBOX_XML}
  {attack_blocks.TOOLBOX_XML}
</xml>
"""

# ── Combined JS Block Definitions ───────────────────────────
BLOCK_DEFINITIONS_JS = (
    structure_blocks.BLOCK_DEFINITIONS_JS
    + recon_blocks.BLOCK_DEFINITIONS_JS
    + attack_blocks.BLOCK_DEFINITIONS_JS
)

# ── Combined JS Python Generators ───────────────────────────
PYTHON_GENERATORS_JS = (
    structure_blocks.PYTHON_GENERATORS_JS
    + recon_blocks.PYTHON_GENERATORS_JS
    + attack_blocks.PYTHON_GENERATORS_JS
)


# ── Unified run_scan() dispatcher ───────────────────────────
# Maps mode strings to backend functions.
# To add a new tool: add the function to the right block file,
# then add one line here. No long if/elif chains needed.

import streamlit as st
from Blocks.recon_blocks import (
    perform_dns_lookup,
    perform_ip_geolocation,
    perform_phone_tracking,
    perform_whois_lookup,
    perform_robots_sitemap_scan,
    perform_ssl_audit,
    perform_shodan_lookup,
    perform_http_header_audit,
    perform_service_enumeration,
    perform_regex_filter,
)
from Blocks.attack_blocks import (
    perform_sql_injection_test,
    perform_xss_payload_test,
    perform_directory_brute_force,
    perform_port_scan,
    perform_credential_attack,
    perform_vulnerability_lookup,
    perform_malware_detection,
    perform_firewall_detect,
    perform_basic_fuzz,
    perform_exploit_simulation,
)

# Simple modes — just need target
_SIMPLE_HANDLERS = {
    "dns":          perform_dns_lookup,
    "geo":          perform_ip_geolocation,
    "phone":        perform_phone_tracking,
    "whois":        perform_whois_lookup,
    "robots":       perform_robots_sitemap_scan,
    "ssl_audit":    perform_ssl_audit,
    "shodan":       perform_shodan_lookup,
    "header_audit": perform_http_header_audit,
    "service_enum": perform_service_enumeration,
    "fuzz":         perform_basic_fuzz,
    "exploit":      perform_exploit_simulation,
    "firewall_detect": perform_firewall_detect,
}


def run_scan(target: str, mode: str, structural: str = None,
             payload: str = None, username: str = None,
             password_list: str = None) -> str:
    """
    Central dispatcher called by all Blockly-generated code.
    Routes to the correct backend function based on mode string.
    """
    if mode in _SIMPLE_HANDLERS:
        res = _SIMPLE_HANDLERS[mode](target)

    elif mode == "regex" and structural:
        res = perform_regex_filter(target, structural)

    elif mode == "sql_injection" and payload:
        res = perform_sql_injection_test(target, payload)

    elif mode == "xss_attack" and payload:
        res = perform_xss_payload_test(target, payload)

    elif mode == "directory_brute":
        res = perform_directory_brute_force(target, structural or "")

    elif mode == "port_scan" and structural:
        res = perform_port_scan(target, structural)

    elif mode == "credential_attack" and username and password_list:
        res = perform_credential_attack(target, username, password_list)

    elif mode == "vuln_lookup":
        res = perform_vulnerability_lookup(target, structural or "")

    elif mode == "malware_detect" and structural:
        res = perform_malware_detection(target, structural)

    else:
        res = f"⚠️ Unknown or incomplete mode: '{mode}'"

    # Append to terminal output in session state
    st.session_state["terminal_history_output"] += (
        f"\n[ENGINE] Module → {mode.upper()}\n{res}\n"
    )
    return res
