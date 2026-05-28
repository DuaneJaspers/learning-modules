import json
import os
import re

def fix_cryptography():
    path = "modules/cryptography-basics/module.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Fix assessment
    mcq_ids = []
    for s in data['sections']:
        for e in s['exercises']:
            if e['type'] == 'mcq': mcq_ids.append(e['id'])
    
    data['assessment']['exercises'] = [
        {"exerciseId": mcq_ids[1], "weight": 1.0}, # protocol-mcq
        {"exerciseId": mcq_ids[0], "weight": 1.0}, # caesar-mcq
        {"exerciseId": mcq_ids[2], "weight": 1.0}, # quantum-mcq
        {"exerciseId": mcq_ids[1], "weight": 1.0}, # protocol-mcq (reuse)
        {"exerciseId": mcq_ids[1], "weight": 1.0}, # protocol-mcq (reuse)
    ]
    
    # Fix error spotting
    for s in data['sections']:
        for e in s['exercises']:
            if e['type'] == 'error_spotting':
                e['content'] = e['content'].replace(
                    "Therefore, RSA can never be broken and we should use it for everything.",
                    "Therefore, RSA can never be broken [ERROR:1] and we should use it for everything [ERROR:2]."
                )
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Fixed cryptography-basics")

def fix_fall_of_rome():
    path = "modules/fall-of-rome/module.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mcq_ids = []
    for s in data['sections']:
        for e in s['exercises']:
            if e['type'] == 'mcq': mcq_ids.append(e['id'])
    
    data['assessment']['exercises'] = [
        {"exerciseId": mcq_ids[0], "weight": 1.0},
        {"exerciseId": mcq_ids[1], "weight": 1.0},
        {"exerciseId": mcq_ids[2], "weight": 1.0},
        {"exerciseId": mcq_ids[0], "weight": 1.0},
    ]
    
    for s in data['sections']:
        for e in s['exercises']:
            if e['type'] == 'error_spotting':
                e['content'] = e['content'].replace(
                    "If the Germanic tribes and Persians had not attacked, the Roman Empire would have continued to thrive.",
                    "If the Germanic tribes and Persians had not attacked, the Roman Empire would have continued to thrive [ERROR:1]."
                ).replace(
                    "The internal problems were just excuses that weak emperors used to justify their failures.",
                    "The internal problems were just excuses that weak emperors used to justify their failures [ERROR:2]."
                )
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Fixed fall-of-rome")

def fix_sample_logic():
    path = "modules/sample-logic/module.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mcq_ids = []
    for s in data['sections']:
        for e in s['exercises']:
            if e['type'] == 'mcq': mcq_ids.append(e['id'])
    
    data['assessment']['exercises'] = [
        {"exerciseId": mcq_ids[0], "weight": 1.0},
        {"exerciseId": mcq_ids[1], "weight": 1.0},
    ]
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Fixed sample-logic")

def fix_scientific_rev():
    path = "modules/scientific-revolution/module.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mcq_ids = []
    for s in data['sections']:
        for e in s['exercises']:
            if e['type'] == 'mcq': mcq_ids.append(e['id'])
    
    data['assessment']['exercises'] = [
        {"exerciseId": mcq_ids[0], "weight": 1.0},
        {"exerciseId": mcq_ids[1], "weight": 1.0},
        {"exerciseId": mcq_ids[2], "weight": 1.0},
    ]
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Fixed scientific-revolution")

# Run fixes
fix_cryptography()
fix_fall_of_rome()
fix_sample_logic()
fix_scientific_rev()

# Cleanup script
os.remove("fix_modules.py")
print("\nAll modules fixed and script cleaned up.")
