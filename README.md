# Meeting Intelligence Dashboard

Дашборд для команды — анализ рабочих встреч через Claude API.

## Структура файлов

```
meeting-dashboard/
├── index.html          ← публичный дашборд (ссылка для команды)
├── admin.html          ← форма добавления (только для тебя, локально)
├── update_index.py     ← скрипт обновления индекса
└── meetings/
    ├── index.json      ← список всех встреч (автообновляется)
    └── 2025-05-01-weekly-sync.json   ← каждый митинг = файл
```

---

## Первоначальная настройка (один раз)

### 1. Создай репозиторий на GitHub

- Зайди на github.com → New repository
- Название: `meeting-intelligence` (или любое)
- Visibility: **Public** (нужно для GitHub Pages)
- Нажми Create repository

### 2. Загрузи файлы

```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/ТВО_ИМЯ/meeting-intelligence.git
git push -u origin main
```

### 3. Включи GitHub Pages

- Репозиторий → Settings → Pages
- Source: **Deploy from a branch**
- Branch: `main`, папка: `/ (root)`
- Сохрани → через минуту появится ссылка вида:
  `https://твоё-имя.github.io/meeting-intelligence/`

Эту ссылку даёшь команде и руководителю.

---

## Добавление нового митинга (каждый раз)

### Вариант A — через admin.html (рекомендуется)

1. Открой `admin.html` локально в браузере (просто двойной клик на файл)
2. Введи API ключ (один раз, сохраняется в браузере)
3. Вставь Summary и Транскрипт из Fathom
4. Нажми "Обработать через Claude"
5. Скопируй результат — там будет два JSON блока

### Вариант B — через Claude.ai

Можно просто вставить транскрипт в чат и попросить Claude вернуть JSON в нужном формате.

---

## Сохранение результата в репозиторий

После получения JSON из admin.html:

**Шаг 1** — создай файл митинга:
```
meetings/2025-05-01-название.json
```
Вставь первый JSON блок (данные митинга).

**Шаг 2** — обнови индекс автоматически:
```bash
python3 update_index.py
```

**Шаг 3** — запушь:
```bash
git add meetings/
git commit -m "add meeting: название"
git push
```

Дашборд обновится через ~30 секунд.

---

## API ключ

Получить на: https://console.anthropic.com/api-keys

Стоимость: ~$0.003-0.01 за один митинг (очень дёшево).

API ключ хранится только в твоём браузере (localStorage), в репозиторий не попадает.

---

## Доступ

- **Команда/руководитель**: `https://твоё-имя.github.io/meeting-intelligence/`
- **Добавление митингов**: только ты, локально через `admin.html`
