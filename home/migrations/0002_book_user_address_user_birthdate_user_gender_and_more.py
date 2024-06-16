# Generated by Django 4.2.11 on 2024-03-13 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='UNTITLED', max_length=200)),
                ('author', models.CharField(default='UNKNOWN', max_length=200)),
                ('type', models.IntegerField(choices=[(0, 'article'), (1, 'book'), (2, 'magazine'), (3, 'video/audio'), (4, 'comic'), (5, 'other')])),
                ('liteCate', models.BooleanField(blank=True, default=False)),
                ('socieCate', models.BooleanField(blank=True, default=False)),
                ('naturCate', models.BooleanField(blank=True, default=False)),
                ('techCate', models.BooleanField(blank=True, default=False)),
                ('poliCate', models.BooleanField(blank=True, default=False)),
                ('romanCate', models.BooleanField(blank=True, default=False)),
                ('enterCate', models.BooleanField(blank=True, default=False)),
                ('otherCate', models.BooleanField(blank=True, default=False)),
                ('language', models.CharField(max_length=200, null=True)),
                ('description', models.TextField(max_length=1500, null=True)),
                ('coverImage', models.ImageField(null=True, upload_to='book/coverImage')),
                ('publisher', models.CharField(max_length=200, null=True)),
                ('publication', models.DateField(null=True)),
                ('codeISBN', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='birthdate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.IntegerField(choices=[(0, 'male'), (1, 'female'), (2, 'other')], default=2),
        ),
        migrations.AddField(
            model_name='user',
            name='phoneNum',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.IntegerField(choices=[(0, 'user'), (1, 'moderator'), (2, 'admin'), (3, 'banned')], default=0),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(null=True, validators=[home.models.Review.validateRating])),
                ('review', models.TextField(max_length=1500, null=True)),
                ('bookID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.book')),
                ('userID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Copy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'hidden'), (1, 'available'), (2, 'borrowed'), (3, 'unavailable')], default='hidden', null=True)),
                ('note', models.CharField(max_length=200)),
                ('regDate', models.DateTimeField()),
                ('bookID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.book')),
                ('userID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Borrowance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowDate', models.DateTimeField()),
                ('expiredDate', models.DateTimeField()),
                ('status', models.IntegerField(choices=[(0, 'request'), (1, 'double-check'), (2, 'borrowing'), (3, 'returned'), (4, 'overdue'), (5, 'lost')], default=0)),
                ('deposit', models.FloatField(default=0, null=True)),
                ('copyID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.copy')),
                ('userID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
