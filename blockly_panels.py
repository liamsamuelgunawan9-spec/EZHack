"""Helper utilities for monitoring and stabilizing Blockly toolbox panel open/close behavior.

Usage:
- Import the module in `Main.py` and include the string returned by
  `instrumentation_js()` inside the embedded HTML payload after Blockly is injected.

Example insertion in the HTML payload (inside the <script> where Blockly is initialized):

<script>
  // existing Blockly init...
  {blockly_panels.INSTRUMENTATION_JS}
</script>

The instrumentation adds logging, a MutationObserver on the flyout DOM, and attempts
lightweight reflows/resizes when toolbox state changes. It is non-invasive and only
acts when a `window.workspace` and toolbox/flyout are present.
"""


from pathlib import Path


def instrumentation_js():
    """Return the standalone JS helper source for Blockly panel instrumentation."""
    js_path = Path(__file__).with_suffix('.js')
    return js_path.read_text(encoding='utf-8')


if __name__ == '__main__':
    print(instrumentation_js())
