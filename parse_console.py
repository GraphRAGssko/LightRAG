import json
import re

try:
    with open('rag_storage/console.log', 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"File length: {len(content)}")
    
    # Try to extract the JSON object
    # Look for the pattern {"state":{...}}
    match = re.search(r'(\{"state":\{.*?\})\s*$', content, re.DOTALL)
    if match:
        json_str = match.group(1)
        print("Found JSON match!")
        
        # Test if it's valid JSON
        try:
            data = json.loads(json_str)
            print("Successfully parsed JSON!")
            print(f"Retrieval history items: {len(data.get('state', {}).get('retrievalHistory', []))}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            # Try to fix common issues
            # E.g. unescaped quotes, newlines in strings
    else:
        print("Could not find {\"state\":...} pattern")
        print("Preview of file start:", content[:200])
        print("Preview of file end:", content[-200:])
        
except Exception as e:
    print(f"Error: {e}")
