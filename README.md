Klinika — Run Guide

1) Create and activate venv (Windows)

    python -m venv .venv
    .\.venv\Scripts\activate

2) Install dependencies

    pip install -r requirements.txt

   If install fails due to Python version, use Python 3.12 and recreate the venv.

3) PostgreSQL setup (once)

   - Install PostgreSQL locally and ensure `psql` works.
   - Create database and user (example):

        psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE klinika_db;"
        psql -U postgres -h localhost -p 5432 -c "ALTER USER postgres WITH PASSWORD 'your_password';"

     Or create a dedicated user:

        psql -U postgres -h localhost -p 5432 -c "CREATE USER klinika_user WITH PASSWORD 'your_password';"
        psql -U postgres -h localhost -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE klinika_db TO klinika_user;"

   - Copy `.env.example` to `.env` and set values:

        copy .env.example .env
        REM then edit .env and set DJANGO_SECRET_KEY, DB_*

   Notes
   - The project uses psycopg2 (`psycopg2-binary`) for PostgreSQL.
   - You can enable SSL or other options via `DB_OPTIONS`, e.g. `DB_OPTIONS=sslmode=require`.
   - Persistent connections can be tuned via `DB_CONN_MAX_AGE` (default 60 seconds).

4) Apply migrations and run

    python manage.py migrate
    python manage.py runserver

Notes
- If you see "ModuleNotFoundError: No module named 'django'", dependencies are not installed in the active venv. Re‑activate venv and run step 2.
- If you use file/image uploads, Pillow is required and included in requirements.txt.
- If NoReverseMatch occurs, verify URL names used in redirect() exist in patients/urls.py.
