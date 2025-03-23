import re

def prepare_markdown_response(response_text):
    """Ensures response is properly formatted as clean markdown."""
    # Remove any trailing ellipses and complete sentences
    if response_text.strip().endswith('...'):
        response_text = response_text.strip()[:-3] + '.'
    
    # Ensure proper line breaks between list items
    response_text = re.sub(r'(\n\s*-\s+)', r'\n\n- ', response_text)
    
    # Make sure headings have proper spacing
    response_text = re.sub(r'##(?=\S)', r'## ', response_text)
    
    return response_text

# Then in your Flask endpoint:
@app.route('/api/query', methods=['POST'])
def process_query():
    # ... existing code ...
    
    # Before returning the response, beautify it
    if result and 'final_response' in result:
        result['final_response'] = prepare_markdown_response(result['final_response'])
    
    # Return the beautified response
    return jsonify(result) 