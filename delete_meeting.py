#!/usr/bin/env python3
"""
delete_meeting.py — удаляет митинг одной командой.

Использование:
  python delete_meeting.py 2025-04-29-название.json
"""
import json
import os
import sys
import glob
import subprocess

MEETINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meetings')
INDEX_PATH = os.path.join(MEETINGS_DIR, 'index.json')

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Ошибка: {result.stderr.strip()}")
    return result.returncode == 0

def rebuild_index():
    entries = []
    for filepath in sorted(glob.glob(os.path.join(MEETINGS_DIR, '*.json'))):
        filename = os.path.basename(filepath)
        if filename == 'index.json':
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                m = json.load(f)
            analysis = m.get('analysis', {})
            summary = analysis.get('summary', '') or analysis.get('purpose', '')
            entries.append({
                'file': filename,
                'title': m.get('title', ''),
                'date': m.get('date', ''),
                'participants': m.get('participants', ''),
                'summary_preview': summary[:120] + '...' if len(summary) > 120 else summary,
                'tasks_count': len(analysis.get('tasks', [])),
                'resolved_count': len(analysis.get('resolved', [])),
                'open_count': len(analysis.get('open_questions', []))
            })
        except Exception as e:
            print(f"  Пропускаю {filename}: {e}")
    entries.sort(key=lambda x: x.get('date', ''), reverse=True)
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    return len(entries)

def main():
    if len(sys.argv) < 2:
        print("Использование: python delete_meeting.py FILENAME.json")
        print("\nДоступные митинги:")
        for f in sorted(glob.glob(os.path.join(MEETINGS_DIR, '*.json'))):
            name = os.path.basename(f)
            if name != 'index.json':
                print(f"  {name}")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.json'):
        filename += '.json'

    filepath = os.path.join(MEETINGS_DIR, filename)

    if not os.path.exists(filepath):
        print(f"Файл не найден: meetings/{filename}")
        sys.exit(1)

    # Read title before deleting
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        title = data.get('title', filename)
    except:
        title = filename

    print(f"\n  Удаляю: {filename}")
    print(f"  Встреча: {title}")

    os.remove(filepath)
    count = rebuild_index()

    print(f"  index.json обновлён — осталось {count} встреч")
    print("\n  Пушу в GitHub...")

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run('git add meetings/')
    run(f'git commit -m "remove meeting: {title}"')
    ok = run('git push')

    print()
    if ok:
        print("  Готово! Дашборд обновится через ~1 минуту.")
        print("  https://dmitriilitvin.github.io/meeting-intelligence/")
    else:
        print("  Push не удался — проверь подключение.")
    print()

if __name__ == '__main__':
    main()
