# Generated by Django 4.0.4 on 2022-04-16 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lostandfound', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lostfounditem',
            name='status',
            field=models.CharField(default='Unhandled', max_length=10),
            preserve_default=False,
        ),
    ]
