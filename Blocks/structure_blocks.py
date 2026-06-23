# ============================================================
# STRUCTURE BLOCKS
# Covers: Sequence trigger, Wait, and all Target Input blocks
# ============================================================

# ── Python backend ───────────────────────────────────────────
# Structure blocks don't need Python functions — they are
# control-flow only. The sequence trigger and wait blocks
# emit time.sleep() and comments directly via the JS generators.

# ── Toolbox XML ─────────────────────────────────────────────
TOOLBOX_XML = """
    <category name="🏁 Sequence Triggers" colour="0">
      <block type="when_sequence_activated"></block>
    </category>

    <category name="🔁 Loops &amp; Wait" colour="120">
      <block type="controls_repeat_ext">
        <value name="TIMES">
          <shadow type="math_number">
            <field name="NUM">5</field>
          </shadow>
        </value>
      </block>
      <block type="controls_whileUntil"></block>
      <block type="action_wait_task"></block>
    </category>

    <category name="🧠 Core Logic" colour="210">
      <block type="controls_if"></block>
      <block type="logic_compare"></block>
      <block type="logic_operation"></block>
      <block type="logic_negate"></block>
      <block type="logic_boolean"></block>
    </category>

    <category name="🔢 Math &amp; Data" colour="230">
      <block type="math_number"></block>
      <block type="math_arithmetic"></block>
      <block type="text"></block>
      <block type="text_print"></block>
    </category>

    <category name="🌐 Core Inputs" colour="160">
      <block type="custom_input_string"></block>
      <block type="global_phone_preset"></block>
      <block type="custom_phone_signature"></block>
    </category>
"""

# ── Block definitions (JS) ───────────────────────────────────
BLOCK_DEFINITIONS_JS = """
    // --- SEQUENCE TRIGGER ---
    Blockly.Blocks['when_sequence_activated'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("🚀 SEQUENCE GENERATOR")
            .appendField(new Blockly.FieldTextInput("passive_recon_agent"), "SEQUENCE_ID");
        this.setNextStatement(true, null);
        this.setColour(0);
        this.setTooltip("Right-click to activate this sequence block.");
        this.setOnChange(function(event) {
            if (!event || event.type !== Blockly.Events.BLOCK_CHANGE) return;
            if (event.blockId !== this.id) return;
            if (event.name !== "SEQUENCE_ID") return;
            this.pendingRunLabel_ = this.getFieldValue("SEQUENCE_ID");
        });
      },
      customContextMenu: function(options) {
          var currentBlockInstance = this;
          var activateOption = {
              enabled: true,
              text: "⚡ Activate This Sequence",
              callback: function() {
                  var targetedSequencePayload = window.ezCompileSequences ? window.ezCompileSequences() : Blockly.Python.workspaceToCode(window.workspace);
                  var sequenceIdentifier = currentBlockInstance.getFieldValue("SEQUENCE_ID");
                  var xmlDom = Blockly.Xml.workspaceToDom(window.workspace);
                  var currentXmlText = Blockly.Xml.domToText(xmlDom);
                  window.ezSendState("run", {
                      code: targetedSequencePayload,
                      xml: currentXmlText,
                      sequenceId: sequenceIdentifier
                  });
              }
          };
          options.push(activateOption);
      }
    };

    // --- WAIT ---
    Blockly.Blocks['action_wait_task'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("⏳ Wait for")
            .appendField(new Blockly.FieldNumber(1, 0, 60), "SECONDS")
            .appendField("seconds");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
        this.setTooltip("Pauses execution for a fixed number of seconds.");
      }
    };

    // --- DOMAIN / URL INPUT ---
    Blockly.Blocks['custom_input_string'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("Target Domain:")
            .appendField(new Blockly.FieldTextInput("google.com"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
        this.setTooltip("Provide a target domain, URL, or raw string.");
      }
    };

    // --- PRESET PHONE (dropdown country code) ---
    Blockly.Blocks['global_phone_preset'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("📱 Preset Phone Target")
            .appendField(new Blockly.FieldDropdown([
                ["🇮🇩 +62", "+62"],
                ["🇺🇸 +1",  "+1"],
                ["🇬🇧 +44", "+44"]
            ]), "CC_PREFIX")
            .appendField(new Blockly.FieldTextInput("8123456789"), "PHONE_BODY");
        this.setOutput(true, "String");
        this.setColour(160);
        this.setTooltip("Select a country prefix and enter a phone number.");
      }
    };

    // --- CUSTOM PHONE (manual country code) ---
    Blockly.Blocks['custom_phone_signature'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("🏳️ Custom Country Code")
            .appendField(new Blockly.FieldTextInput("+61"), "CUSTOM_PREFIX")
            .appendField("Number:")
            .appendField(new Blockly.FieldTextInput("412345678"), "PHONE_BODY");
        this.setOutput(true, "String");
        this.setColour(160);
        this.setTooltip("Enter a custom international country code and phone number.");
      }
    };
"""

# ── Python generators (JS) ───────────────────────────────────
PYTHON_GENERATORS_JS = """
    Blockly.Python['when_sequence_activated'] = function(block) {
        var seqId = block.getFieldValue('SEQUENCE_ID');
        return '# Sequence: ' + seqId + '\\n';
    };

    Blockly.Python['action_wait_task'] = function(block) {
        return 'time.sleep(' + block.getFieldValue('SECONDS') + ')\\n';
    };

    Blockly.Python['custom_input_string'] = function(block) {
        return [JSON.stringify(block.getFieldValue('RAW_TEXT')), Blockly.Python.ORDER_ATOMIC];
    };

    Blockly.Python['global_phone_preset'] = function(block) {
        return [
            JSON.stringify(block.getFieldValue('CC_PREFIX') + block.getFieldValue('PHONE_BODY')),
            Blockly.Python.ORDER_ATOMIC
        ];
    };

    Blockly.Python['custom_phone_signature'] = function(block) {
        var prefix = block.getFieldValue('CUSTOM_PREFIX').trim();
        if (!prefix.startsWith("+")) { prefix = "+" + prefix; }
        return [
            JSON.stringify(prefix + block.getFieldValue('PHONE_BODY').trim()),
            Blockly.Python.ORDER_ATOMIC
        ];
    };
"""