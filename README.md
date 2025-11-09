Klinika — Run Guide

1) Create and activate venv (Windows)

    python -m venv .venv
    .\.venv\Scripts\activate

2) Install dependencies

    pip install -r requirements.txt

   If install fails due to Python version, use Python 3.12 and recreate the venv.

3) Apply migrations and run

    python manage.py migrate
    python manage.py runserver

Notes
- If you see "ModuleNotFoundError: No module named 'django'", dependencies are not installed in the active venv. Re‑activate venv and run step 2.
- If you use file/image uploads, Pillow is required and included in requirements.txt.
- If NoReverseMatch occurs, verify URL names used in redirect() exist in patients/urls.py.
