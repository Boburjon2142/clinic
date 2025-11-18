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

PythonAnywhere (Free) deploy checklist
--------------------------------------
1. Upload or clone the project into `/home/<username>/klinika` and create a virtualenv:

       mkvirtualenv --python=python3.12 klinikaenv
       workon klinikaenv
       pip install -r /home/<username>/klinika/requirements.txt

   Install the MySQL driver if you use PythonAnywhere’s MySQL:

       pip install mysqlclient

2. Copy `.env.pythonanywhere` to `.env` and replace placeholders:
   - `DJANGO_SECRET_KEY` with a long random value.
   - `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` with `yourusername.pythonanywhere.com` (plus any custom domain).
   - `DATABASE_URL` with the MySQL credentials shown on the PythonAnywhere Databases tab.
   - Update `STATIC_ROOT` / `MEDIA_ROOT` paths to match `/home/<username>/klinika/...`.

3. Apply migrations, collect static files, and create an admin account:

       workon klinikaenv
       cd /home/<username>/klinika
       python manage.py migrate
       python manage.py collectstatic --noinput
       python manage.py createsuperuser

4. Configure the web app (Manual config, Python 3.12):
   - Code directory: `/home/<username>/klinika`
   - Virtualenv: `/home/<username>/.virtualenvs/klinikaenv`
   - WSGI file loads `klinika_project.wsgi`
   - Static mappings:
        * `/static/` → `/home/<username>/klinika/staticfiles`
        * `/media/` → `/home/<username>/klinika/media`

5. Reload the web app, open the site, and verify `/accounts/login/` works. Use
   `python manage.py check --deploy` in a console to confirm production settings.
