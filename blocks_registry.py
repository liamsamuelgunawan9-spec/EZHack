# ============================================================
# blocks_registry.py — thin re-export shim
# Main.py imports from here, so this file stays as-is.
# All real code now lives in Blocks/
# ============================================================

from Blocks import TOOLBOX_XML, BLOCK_DEFINITIONS_JS, PYTHON_GENERATORS_JS, run_scan

__all__ = ["TOOLBOX_XML", "BLOCK_DEFINITIONS_JS", "PYTHON_GENERATORS_JS", "run_scan"]
