# Project Manager (Django) — Advanced (v3.2)

All features + fixes:
- Tasks, Kanban (no custom tags), collaborators & roles
- Role-based permissions; **permissions fix for task routes**
- REST API (DRF)
- PostgreSQL + Docker
- Logout via POST + CSRF
- Initial migrations included
- **Members page fix**: ensures `self.object` is set even if the form is invalid, preventing AttributeError

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
