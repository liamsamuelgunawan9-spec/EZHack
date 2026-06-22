# ============================================================
# Blocks/__init__.py
# Assembles all three block modules.
# Uses relative imports — safe on Streamlit Cloud.
# Streamlit imported lazily inside run_scan() only.
# ============================================================

from . import structure_blocks, recon_blocks, attack_blocks

TOOLBOX_XML = (
    '<xml id="toolbox" style="display: none">'
    + structure_blocks.TOOLBOX_XML
    + recon_blocks.TOOLBOX_XML
    + attack_blocks.TOOLBOX_XML
    + '</xml>'
)

BLOCK_DEFINITIONS_JS = (
    structure_blocks.BLOCK_DEFINITIONS_JS
    + recon_blocks.BLOCK_DEFINITIONS_JS
    + attack_blocks.BLOCK_DEFINITIONS_JS
)

PYTHON_GENERATORS_JS = (
    structure_blocks.PYTHON_GENERATORS_JS
    + recon_blocks.PYTHON_GENERATORS_JS
    + attack_blocks.PYTHON_GENERATORS_JS
)

from .recon_blocks import (
    perform_dns_lookup, perform_ip_geolocation, perform_phone_tracking,
    perform_whois_lookup, perform_robots_sitemap_scan, perform_ssl_audit,
    perform_shodan_lookup, perform_http_header_audit, perform_service_enumeration,
    perform_regex_filter, perform_reverse_dns_lookup, perform_hostname_parse,
    perform_dns_cache_check, perform_email_parse,
)
from .attack_blocks import (
    perform_port_scan, perform_directory_probe,
    perform_sql_error_detection, perform_xss_reflection_check,
    perform_firewall_detect, perform_malware_hash_check,
)

_SIMPLE_HANDLERS = {
    "dns":              perform_dns_lookup,
    "reverse_dns":      perform_reverse_dns_lookup,
    "hostname_parse":   perform_hostname_parse,
    "dns_cache":        perform_dns_cache_check,
    "geo":              perform_ip_geolocation,
    "phone":            perform_phone_tracking,
    "email_parse":      perform_email_parse,
    "whois":            perform_whois_lookup,
    "robots":           perform_robots_sitemap_scan,
    "ssl_audit":        perform_ssl_audit,
    "shodan":           perform_shodan_lookup,
    "header_audit":     perform_http_header_audit,
    "service_enum":     perform_service_enumeration,
    "firewall_detect":  perform_firewall_detect,
}


def run_scan(target: str, mode: str, structural: str = None,
             payload: str = None, **kwargs) -> str:
    import streamlit as st  # lazy — never fires at import time

    if mode in _SIMPLE_HANDLERS:
        res = _SIMPLE_HANDLERS[mode](target)
    elif mode == "regex" and structural:
        res = perform_regex_filter(target, structural)
    elif mode == "port_scan" and structural:
        res = perform_port_scan(target, structural)
    elif mode == "directory_probe":
        res = perform_directory_probe(target, structural or "")
    elif mode == "sql_error_detect" and payload:
        res = perform_sql_error_detection(target, payload)
    elif mode == "xss_reflect_check" and payload:
        res = perform_xss_reflection_check(target, payload)
    elif mode == "malware_hash_check" and structural:
        res = perform_malware_hash_check(target, structural)
    else:
        res = f"⚠️ Unknown or incomplete scan mode: '{mode}'"

    st.session_state["terminal"] = st.session_state.get("terminal", "")
    st.session_state["terminal"] += (
        f"\n[ENGINE] {mode.upper()}\n{res}\n"
    )
    return res