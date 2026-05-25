python.pythonGenerator.forBlock['target'] = function(block, generator) {
  var field_target = block.getFieldValue('Target');
  // Enclosing the raw text in quotes ensures Python treats it as a clean string literal
  var code = '"' + field_target + '"';
  return [code, python.Order.ATOMIC];
};