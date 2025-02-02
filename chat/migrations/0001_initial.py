# Generated by Django 3.2.6 on 2024-06-20 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_id', models.IntegerField(blank=True, null=True)),
                ('thread_name', models.CharField(blank=True, max_length=20, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('message_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
