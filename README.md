# Klinika — Qabul va To'lov tizimi

Loyiha: tibbiyot klinikasida qabulga yozish, navbatni kuzatish, statistikalar va to'lov kvitansiyasi.

## Tez start

1) Virtual muhitni yoqing va kerakli paketlarni o'rnating:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2) Ma'lumotlar bazasini tayyorlang va admin yarating:

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

3) Serverni ishga tushiring:

```
python manage.py runserver
```

4) Brauzerda:
- `http://127.0.0.1:8000/accounts/login/` — kirish
- `http://127.0.0.1:8000/admin/dashboard/` — admin panel
- `http://127.0.0.1:8000/admin/doctors/` — shifokorlar
- `http://127.0.0.1:8000/patients/` — bemorlar
- `http://127.0.0.1:8000/appointments/` — qabul

## Rollar

`accounts.models.User.role` — `creator|admin|doctor|staff`.

- Creator — to'liq huquqlar
- Admin — tizim boshqaruvi (lekin yangi admin yaratmaydi)
- Doctor — o'z navbat sahifasi
- Staff — registrator (qabul va to'lov)

## PDF kvitansiya (WeasyPrint)

WeasyPrint Windowsda qo'shimcha tizim kutubxonalarini talab qilishi mumkin. Agar PDF generatsiya ishlamasa, ko'rinish HTML qaytaradi. PDF uchun quyidagilar kerak bo'lishi mumkin:
- Visual C++ Redistributable
- GTK/WeasyPrint deps (qarang: https://weasyprint.org/)

## Eslatma

- Hozircha shifokor foydalanuvchi bog'lanishi soddalashtirilgan. Real tizimda Doctor modeliga `user = OneToOneField(User,...)` qo'shish va cheklovlarni shunga ko'ra qilish tavsiya.
- Statistika uchun minimal jadval bor; grafiklar uchun Chart.js qo'shish mumkin.

## Muhit sozlamalari (.env)

Quyidagi faylni yarating va maxfiy saqlang (commit qilmang):

```
# .env
DJANGO_SECRET_KEY=change-me   # majburiy
DB_NAME=klinika_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=127.0.0.1,localhost  # prod uchun domenlarni vergul bilan yozing
```

Eslatma: `.env` fayli `.gitignore`ga kiritilgan.

## Pushga tayyorlash

- `.gitignore` qo'shildi: `venv/`, `__pycache__/`, `media/`, `staticfiles/`, `.vscode/`, `.env` va boshqalar ignor qilinadi.
- `.env.example` qo'shildi — namunaviy sozlamalar.
- `.env`da `DJANGO_SECRET_KEY` va `ALLOWED_HOSTS` ni albatta to'ldiring.
- PostgreSQL uchun sozlamalarni to'ldiring va bazani ishga tushiring.
- Migratsiyalar: `python manage.py makemigrations && python manage.py migrate`
- (ixtiyoriy) Statiklar: `python manage.py collectstatic`
- Keyin gitga tayyorlang:

```
git init
git add .
git commit -m "Initial commit"
```
