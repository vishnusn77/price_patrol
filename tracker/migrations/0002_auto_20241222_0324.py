# Generated by Django 3.1.12 on 2024-12-22 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.CharField(default='Anonymous', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='user_email',
            field=models.EmailField(default='anonymous@example.com', max_length=254),
        ),
    ]
