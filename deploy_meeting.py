#!/usr/bin/env python3
"""
deploy_meeting.py — добавляет митинг одной командой.

Использование:
  python deploy_meeting.py

Скрипт попросит вставить JSON из admin.html,
затем сам создаст файл, обновит index.json и запушит в GitHub.
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
            summary = analysis.get('summary', '')
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
    print("=" * 55)
    print("  Meeting Intelligence — Добавить встречу")
    print("=" * 55)
    print()
    print("Вставь JSON из admin.html (только первый блок,")
    print('начинающийся с "{"), затем нажми Enter два раза:')
    print()

    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if line == '':
                empty_count += 1
                if empty_count >= 2 and lines:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break

    raw = '\n'.join(lines).strip()

    # Strip comment lines
    clean_lines = [l for l in raw.split('\n') if not l.strip().startswith('//')]
    raw = '\n'.join(clean_lines).strip()

    # If there are two JSON blocks, take only the first
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract first JSON object
        depth = 0
        start = raw.find('{')
        end = -1
        for i, ch in enumerate(raw[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end == -1:
            print("\nОшибка: не удалось разобрать JSON. Попробуй ещё раз.")
            sys.exit(1)
        try:
            data = json.loads(raw[start:end])
        except json.JSONDecodeError as e:
            print(f"\nОшибка JSON: {e}")
            sys.exit(1)

    meeting_id = data.get('id', '')
    title = data.get('title', 'Встреча')
    date = data.get('date', '')

    if not meeting_id:
        print("\nОшибка: в JSON нет поля 'id'")
        sys.exit(1)

    filename = meeting_id + '.json'
    filepath = os.path.join(MEETINGS_DIR, filename)

    # Save meeting file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  Файл сохранён: meetings/{filename}")

    # Rebuild index
    count = rebuild_index()
    print(f"  index.json обновлён — {count} встреч")

    # Git
    print("\n  Пушу в GitHub...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run('git add meetings/')
    run(f'git commit -m "add meeting: {title}"')
    ok = run('git push')

    print()
    if ok:
        print("  Готово! Дашборд обновится через ~1 минуту.")
        print(f"  https://dmitriilitvin.github.io/meeting-intelligence/")
    else:
        print("  Push не удался — проверь подключение к интернету.")
    print()

if __name__ == '__main__':
    main()
