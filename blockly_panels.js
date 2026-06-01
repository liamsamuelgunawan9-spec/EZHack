(function(){
  function log(){
    try{ console.debug('[BLOCKLY-PANELS]', ...arguments); }catch(e){}
  }

  function ensureWorkspace(){
    if (window.workspace) return window.workspace;
    if (window.Blockly && Blockly.getMainWorkspace) return Blockly.getMainWorkspace();
    return null;
  }

  function patchToolbox(){
    var workspace = ensureWorkspace();
    if (!workspace) {
      log('Workspace unavailable, delaying patch.');
      setTimeout(patchToolbox, 200);
      return;
    }

    var toolbox = workspace.getToolbox ? workspace.getToolbox() : (workspace.toolbox_ || null);
    if (!toolbox) {
      log('Toolbox unavailable, retrying.');
      setTimeout(patchToolbox, 200);
      return;
    }

    log('Patching Blockly toolbox behavior', { toolbox: !!toolbox });

    var customCount = 0;
    var originalSelectItem = toolbox.setSelectedItem;
    if (typeof originalSelectItem === 'function') {
      toolbox.setSelectedItem = function(item) {
        customCount += 1;
        try {
          log('toolbox.setSelectedItem()', { item: item && item.getText && item.getText(), count: customCount });
        } catch (e) {
          log('toolbox.setSelectedItem log failed', e);
        }

        // Prevent stale selection state from surviving after repeated open/close cycles.
        if (this.selectedItem_ && this.selectedItem_ !== item && typeof this.deselectItem_ === 'function') {
          try {
            this.deselectItem_(this.selectedItem_);
          } catch (err) {
            log('deselect previous selectedItem failed', err);
          }
        }

        var result = originalSelectItem.call(this, item);

        try {
          if (window.Blockly && window.Blockly.svgResize) Blockly.svgResize(workspace);
        } catch (err) {
          log('svgResize after setSelectedItem failed', err);
        }

        return result;
      };
      log('toolbox.setSelectedItem patched');
    } else {
      log('toolbox.setSelectedItem not found');
    }

    if (typeof toolbox.clearSelection === 'function') {
      var originalClearSelection = toolbox.clearSelection;
      toolbox.clearSelection = function() {
        log('toolbox.clearSelection()');
        var result = originalClearSelection.call(this);
        try {
          if (window.Blockly && window.Blockly.svgResize) Blockly.svgResize(workspace);
        } catch (err) {
          log('svgResize after clearSelection failed', err);
        }
        return result;
      };
      log('toolbox.clearSelection patched');
    }

    var flyout = toolbox.getFlyout ? toolbox.getFlyout() : (toolbox.flyout_ || null);
    if (flyout) {
      try {
        var observer = new MutationObserver(function(mutations) {
          log('flyout mutation', mutations.length);
          try { if (window.Blockly && window.Blockly.svgResize) Blockly.svgResize(workspace); } catch (e) { log('svgResize on mutation failed', e); }
        });
        observer.observe(document.documentElement, { childList: true, subtree: true });
        log('flyout mutation observer attached');
      } catch (e) {
        log('flyout observer attach failed', e);
      }
    }

    if (typeof toolbox.clearSelection === 'function' && typeof toolbox.setSelectedItem === 'function') {
      var originalClick = document.addEventListener;
      // Keep existing event handling while also logging.
      document.addEventListener('click', function(ev) {
        var row = ev.target.closest && ev.target.closest('.blocklyTreeRow');
        if (!row) return;
        setTimeout(function() {
          try {
            var flyoutNode = document.querySelector('.blocklyFlyout');
            var visible = flyoutNode && flyoutNode.style.display !== 'none';
            log('toolbox row clicked', row.textContent && row.textContent.trim(), { flyoutVisible: !!visible });
            if (!visible) {
              toolbox.clearSelection();
            }
            if (window.Blockly && window.Blockly.svgResize) Blockly.svgResize(workspace);
          } catch (err) {
            log('toolbox row handler failed', err);
          }
        }, 30);
      }, true);
      log('toolbox click logger installed');
    }
  }

  patchToolbox();
})();
