python.pythonGenerator.forBlock['display_result'] = function(block, generator) {
  // Directly passes the active result tracker down to our Streamlit view engine
  var code = 'show_output_to_user(current_result)\n';
  return code;
};