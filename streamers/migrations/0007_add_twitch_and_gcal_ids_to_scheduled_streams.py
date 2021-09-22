# Generated by Django 3.2.7 on 2021-09-14 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("streamers", "0006_add_scheduled_streams"),
    ]

    operations = [
        migrations.AddField(
            model_name="scheduledstream",
            name="google_calendar_event_id",
            field=models.CharField(
                blank=True, max_length=128, null=True, verbose_name="Identifiant interne de l'événement Google Calendar"
            ),
        ),
        migrations.AddField(
            model_name="scheduledstream",
            name="twitch_segment_id",
            field=models.CharField(
                blank=True, max_length=128, null=True, verbose_name="Identifiant interne du segment Twitch"
            ),
        ),
        migrations.AddField(
            model_name="scheduledstream",
            name="weekly",
            field=models.BooleanField(default=False, verbose_name="Est-ce que le stream est hebdomadaire ?"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="scheduledstream",
            name="category",
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name="Catégorie du stream"),
        ),
    ]