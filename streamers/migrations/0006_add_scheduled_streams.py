# Generated by Django 3.2.7 on 2021-09-13 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("streamers", "0005_streamers_store_offline_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScheduledStream",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=140, verbose_name="Titre du stream programmé"),
                ),
                (
                    "start",
                    models.DateTimeField(verbose_name="Heure de début prévue du stream"),
                ),
                (
                    "end",
                    models.DateTimeField(verbose_name="Heure de fin prévue du stream"),
                ),
                (
                    "category",
                    models.CharField(max_length=140, verbose_name="Catégorie du stream"),
                ),
                (
                    "streamer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedule",
                        to="streamers.streamer",
                        verbose_name="Streamer ayant programmé ce stream",
                    ),
                ),
            ],
        ),
    ]