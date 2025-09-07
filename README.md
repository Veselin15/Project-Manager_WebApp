# Project Manager (Django) — Advanced (v3.1)

This build includes all features from v3 plus a fix for member/owner permission checks when task URLs use `pk` (e.g. `/tasks/<id>/edit/`).

## Highlights
- Tasks with due date, status, priority, assignee, and board order
- Kanban board (no custom template tags)
- Collaborators & roles (Owner/Member)
- Role-based permissions (owners manage project & members; members manage tasks)
- REST API (DRF)
- PostgreSQL + Docker
- Logout via POST + CSRF
- Initial migrations included
- **Permissions fix**: correctly resolves project from `Task` pk for task routes

## Run (local, SQLite)
```bash
python -m venv .venv
# Windows: . .venv/Scripts/activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker + Postgres
```bash
docker compose up --build
```

## API
- /api/projects/, /api/tasks/
- Project actions: add_member, remove_member
- Task action: tasks/{id}/move
