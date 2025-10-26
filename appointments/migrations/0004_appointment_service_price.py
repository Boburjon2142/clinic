from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_appointment_doc_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='service_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Xizmat narxi'),
        ),
    ]

