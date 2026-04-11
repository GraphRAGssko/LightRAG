import json

try:
    with open('rag_storage/console.log', 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    data = json.loads(content)
    history = data.get("state", {}).get("retrievalHistory", [])
    
    output_js = f"""// 아래 3줄을 모두 복사해서 10.10.10.16 브라우저의 Console 창에 붙여넣고 엔터를 누르세요!
let currentSettings = JSON.parse(localStorage.getItem('settings-storage') || '{{"state":{{}}}}');
currentSettings.state.retrievalHistory = {json.dumps(history, ensure_ascii=False)};
localStorage.setItem('settings-storage', JSON.stringify(currentSettings));
"""

    with open("rag_storage/run_this.js", "w", encoding="utf-8") as f:
        f.write(output_js)
        
    print(output_js)
except Exception as e:
    print(f"Error: {e}")
