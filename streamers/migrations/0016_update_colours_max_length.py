# Generated by Django 3.2.7 on 2021-09-27 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("streamers", "0015_move_streamers_colours_to_property"),
    ]

    operations = [
        migrations.AlterField(
            model_name="streamer",
            name="_colours",
            field=models.CharField(
                blank=True,
                db_column="colours",
                help_text="Liste de trois couleurs principales à utiliser pour habiller ce/cette streamer/euse. Les valeurs sont stockées sous la forme d'une liste de nombres flottants, dont chaque triplet forme une couleur RGB.",
                max_length=71,
                null=True,
                verbose_name="couleurs",
            ),
        ),
    ]