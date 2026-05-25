python.pythonGenerator.forBlock['action_scan'] = function(block, generator) {
  var dropdown_scantype = block.getFieldValue('SCANTYPE');
  var value_name = generator.valueToCode(block, 'NAME', python.Order.ATOMIC) || "''";
  
  // Compiles down to an assignment executing our core Python backend utility function
  var code = 'current_result = run_utility_scan(' + value_name + ', "' + dropdown_scantype + '")\n';
  return code;
};