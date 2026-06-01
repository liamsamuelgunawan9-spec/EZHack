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


def instrumentation_js():
    """Return a JS string to inject into the Blockly page for toolbox monitoring.

    The string is safe to embed directly inside a <script> tag in the payload.
    """
    js = r'''(function(){
  function log(){
    try{ console.debug('[BLOCKLY-PANELS]', ...arguments); }catch(e){}
  }

  function safeGet(obj, prop){ return obj && (obj[prop] || obj['_' + prop]) || null; }

  function ensureWorkspace(){
    if (window.workspace) return window.workspace;
    if (window.Blockly && Blockly.getMainWorkspace) return Blockly.getMainWorkspace();
    return null;
  }

  var ws = ensureWorkspace();
  if(!ws){ log('No workspace found yet. Attaching on "workspace." events.');
    document.addEventListener('DOMContentLoaded', function(){ setTimeout(runInstrument, 200); });
    setTimeout(runInstrument, 800);
    return;
  }

  function runInstrument(){
    var workspace = ensureWorkspace();
    if(!workspace){ log('Workspace still unavailable.'); return; }
    var toolbox = workspace.getToolbox ? workspace.getToolbox() : (workspace.toolbox_ || null);
    var flyout = toolbox && (toolbox.getFlyout ? toolbox.getFlyout() : (toolbox.flyout_ || null));

    log('Instrumenting toolbox/flyout', { toolbox: !!toolbox, flyout: !!flyout });

    var openCounter = 0;

    // Listen for clicks on toolbox category rows
    document.addEventListener('click', function(ev){
      var row = ev.target.closest && ev.target.closest('.blocklyTreeRow');
      if(!row) return;
      setTimeout(function(){
        try{
          // detect flyout visibility
          var flyoutNode = document.querySelector('.blocklyFlyout');
          var visible = flyoutNode && (flyoutNode.style.display !== 'none');
          if(visible) openCounter++;
          log('Category clicked', row.textContent && row.textContent.trim(), 'openCount=', openCounter);

          // Attempt a gentle repair: call flyout.reflow() and workspace resize
          try{ if(flyout && typeof flyout.reflow === 'function') flyout.reflow(); }catch(err){ log('flyout.reflow error', err); }
          try{ if(window.Blockly && window.Blockly.svgResize) Blockly.svgResize(workspace); }catch(err){ log('svgResize error', err); }

          // If the third open fails (heuristic), force a small toggle to re-create flyout DOM
          if(openCounter > 2){
            try{
              log('Third-open heuristic triggered — forcing temporary toolbox toggle');
              // quick close/open to refresh flyout DOM
              var selected = toolbox && toolbox.getSelectedItem && toolbox.getSelectedItem();
              if(toolbox && typeof toolbox.clearSelection === 'function') toolbox.clearSelection();
              setTimeout(function(){ if(toolbox && selected && typeof toolbox.selectItem === 'function') { try{ toolbox.selectItem(selected); }catch(e){ log('reselect failed', e); } } else if(toolbox && typeof toolbox.rebuild === 'function') { try{ toolbox.rebuild(); }catch(e){ log('toolbox.rebuild failed', e); } } Blockly.svgResize(workspace); }, 30);
            }catch(e){ log('third-open repair failed', e); }
          }

        }catch(e){ log('click-handler error', e); }
      }, 40);
    }, true);

    // Observe flyout DOM for attribute/child changes and trigger svgResize
    var flyoutNode = document.querySelector('.blocklyFlyout');
    if(flyoutNode){
      try{
        var mo = new MutationObserver(function(muts){
          log('flyout mutation', muts.length);
          try{ if(window.Blockly && window.Blockly.svgResize) Blockly.svgResize(workspace); }catch(e){ log('svgResize on mutation failed', e); }
        });
        mo.observe(flyoutNode, { attributes: true, childList: true, subtree: true });
      }catch(e){ log('MutationObserver error', e); }
    }

    // Also hook workspace change events to reset the openCounter when blocks change significantly
    try{
      workspace.addChangeListener(function(evt){
        if(evt.type === Blockly.Events.BLOCK_CREATE || evt.type === Blockly.Events.BLOCK_DELETE){
          // reset heuristic so normal user interactions are counted cleanly
          openCounter = 0;
        }
      });
    }catch(e){ log('workspace listener error', e); }
  }

  function delayedStart(){ setTimeout(runInstrument, 200); }
  delayedStart();
})();'''
    return js


if __name__ == '__main__':
    print('Paste the result of instrumentation_js() into your Blockly HTML payload inside a <script> tag.')
