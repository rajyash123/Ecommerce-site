# Generated by Django 2.2.6 on 2019-10-11 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
