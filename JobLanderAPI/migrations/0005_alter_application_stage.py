# Generated by Django 5.1.1 on 2024-09-17 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JobLanderAPI', '0004_alter_company_careers_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='stage',
            field=models.CharField(choices=[('APPLIED', 'Applied'), ('PHONE_SCREEN', 'Phone Screen'), ('ASSESSMENT', 'Assessment'), ('INTERVIEW', 'Interview'), ('OFFER', 'Offer')], max_length=255),
        ),
    ]
