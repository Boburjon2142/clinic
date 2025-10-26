from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                verbose_name='Rol',
                max_length=20,
                choices=[
                    ('creator', 'Creator'),
                    ('admin', "Admin (To'liq)"),
                    ('admin1', 'Admin 1 (Menejer)'),
                    ('admin2', 'Admin 2 (Narx belgilovchi)'),
                    ('admin3', 'Admin 3 (Kassir)'),
                    ('doctor', 'Shifokor'),
                    ('staff', 'Qabulxona'),
                ],
                default='staff',
            ),
        ),
    ]

