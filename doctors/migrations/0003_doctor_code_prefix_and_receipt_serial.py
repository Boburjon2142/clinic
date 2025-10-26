from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0002_alter_doctor_options_alter_doctor_department_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='code_prefix',
            field=models.CharField(max_length=2, verbose_name='Kvitansiya prefiksi', default='A'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='receipt_serial',
            field=models.PositiveIntegerField(verbose_name="Kvitansiya ketma-ket raqami", default=0),
        ),
    ]

