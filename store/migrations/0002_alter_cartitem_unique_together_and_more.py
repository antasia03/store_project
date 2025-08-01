# Generated by Django 5.1.5 on 2025-03-02 07:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('user', 'product')},
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='size',
        ),
    ]
