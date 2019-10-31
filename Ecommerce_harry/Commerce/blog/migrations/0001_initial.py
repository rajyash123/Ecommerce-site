# Generated by Django 2.2.6 on 2019-10-31 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('post_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=20)),
                ('head0', models.CharField(max_length=500)),
                ('head1', models.CharField(max_length=500)),
                ('head2', models.CharField(max_length=500)),
                ('pub_date', models.DateField()),
                ('subcategory', models.CharField(default='', max_length=20)),
                ('thumbnail', models.ImageField(upload_to='')),
            ],
        ),
    ]
