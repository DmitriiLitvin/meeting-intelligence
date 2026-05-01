#!/usr/bin/env python3
"""
update_index.py — автоматически обновляет meetings/index.json
на основе всех .json файлов в папке meetings/

Запуск: python3 update_index.py
"""
import json
import os
import glob

meetings_dir = os.path.join(os.path.dirname(__file__), 'meetings')
index_path = os.path.join(meetings_dir, 'index.json')

entries = []

for filepath in sorted(glob.glob(os.path.join(meetings_dir, '*.json'))):
    filename = os.path.basename(filepath)
    if filename == 'index.json':
        continue
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            m = json.load(f)
        analysis = m.get('analysis', {})
        summary = analysis.get('summary', '')
        entry = {
            'file': filename,
            'title': m.get('title', ''),
            'date': m.get('date', ''),
            'participants': m.get('participants', ''),
            'summary_preview': summary[:120] + '...' if len(summary) > 120 else summary,
            'tasks_count': len(analysis.get('tasks', [])),
            'resolved_count': len(analysis.get('resolved', [])),
            'open_count': len(analysis.get('open_questions', []))
        }
        entries.append(entry)
        print(f'  ✓ {filename}')
    except Exception as e:
        print(f'  ✗ {filename}: {e}')

entries.sort(key=lambda x: x.get('date', ''), reverse=True)

with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f'\nindex.json обновлён — {len(entries)} встреч')
