import json

# 원본 jsonl 파일과 저장할 짧은 샘플 파일 이름
input_file = "agriculture.jsonl"
output_file = "agriculture_sample.jsonl"

# 데이터 길이 제한 (글자 수)
MAX_CHAR_LIMIT = 500

with open(input_file, 'r', encoding='utf-8') as f_in, \
     open(output_file, 'w', encoding='utf-8') as f_out:
    
    # 첫 번째 줄만 읽기
    line = f_in.readline()
    if line:
        data = json.loads(line)
        
        # 긴 필드(context 등) 자르기
        if 'context' in data and len(data['context']) > MAX_CHAR_LIMIT:
            data['context'] = data['context'][:MAX_CHAR_LIMIT] + "\n\n... [테스트를 위해 뒷부분 생략됨]"
            
        # 다시 jsonl 형태로 저장
        f_out.write(json.dumps(data, ensure_ascii=False) + '\n')

print(f"[{output_file}] 로 샘플 생성이 완료되었습니다.")
