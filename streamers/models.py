import os
from datetime import timedelta
from io import BytesIO

import requests
from django.conf import settings
from django.contrib import admin
from django.core import files
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from pogscience.storage import OverwriteStorage


class User(AbstractUser):
    pass


def image_upload_to(folder):
    """
    Generates a function returning the filename to use for a streamer profile
    picture, or background image, or other. The image will be named against the
    streamer, in the given folder.

    :param folder: The folder where to store the image.
    :return: A function for Django FileField's upload_to.
    """

    def _inner(instance, filename: str):
        """
        Used by Django, returns the filename to use for the streamers' profile
        pictures.
        """
        _, ext = os.path.splitext(filename)
        return f"twitch/{folder}/{instance.twitch_login}{ext}"

    return _inner


def profile_image_upload_to(*args, **kwargs):
    return image_upload_to("profile")(*args, **kwargs)


def background_image_upload_to(*args, **kwargs):
    return image_upload_to("background")(*args, **kwargs)


def live_preview_image_upload_to(*args, **kwargs):
    return image_upload_to("live-preview")(*args, **kwargs)


class Streamer(models.Model):
    """
    A streamer, member of PogScience.
    """

    class Meta:
        verbose_name = _("streamer")
        verbose_name_plural = _("streamers")
        ordering = ["name", "twitch_login"]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_("compte interne du streamer"),
        null=True,
        blank=True,
        default=None,
    )

    name = models.CharField(
        verbose_name=_("nom du streamer"),
        max_length=128,
        help_text=_("Le nom d'affichage du/de la streamer⋅euse"),
    )
    twitch_login = models.CharField(
        verbose_name=_("nom d'utilisateur Twitch"),
        max_length=64,
        help_text=_("Utilisé pour récupérer les informations automatiquement"),
    )
    twitch_id = models.PositiveBigIntegerField(
        verbose_name=_("identifiant numérique Twitch"),
        help_text=_("Utilisé pour récupérer les informations automatiquement"),
    )
    description = models.CharField(
        verbose_name=_("courte description"),
        max_length=512,
        help_text=_("Une courte description affichée par exemple sur la page d'accueil"),
        blank=True,
    )
    long_description = models.TextField(
        verbose_name=_("longue description"),
        help_text=_("Description potentiellement très longue affichée sur la page du streamer ou de la streameuse"),
        blank=True,
    )
    profile_image = models.ImageField(
        verbose_name=_("image de profil"),
        storage=OverwriteStorage(),
        upload_to=profile_image_upload_to,
        null=True,
        blank=True,
    )
    background_image = models.ImageField(
        verbose_name=_("image de fond"),
        storage=OverwriteStorage(),
        upload_to=background_image_upload_to,
        null=True,
        blank=True,
    )

    live = models.BooleanField(
        verbose_name=_("en live actuellement ?"),
        help_text=_("Est-iel en live actuellement ? Mis à jour automatiquement"),
        default=False,
    )
    live_title = models.CharField(
        verbose_name=_("titre du live"),
        max_length=140,
        blank=True,
        null=True,
        default=None,
        help_text=_("Le titre du live en cours, récupéré automatiquement depuis Twitch"),
    )
    live_game_name = models.CharField(
        verbose_name=_("catégorie du stream"),
        max_length=140,
        blank=True,
        null=True,
        default=None,
        help_text=_("La catégorie du live en cours, récupéré automatiquement depuis Twitch"),
    )
    live_preview = models.ImageField(
        verbose_name=_("aperçu du live"),
        storage=OverwriteStorage(),
        upload_to=live_preview_image_upload_to,
        null=True,
        blank=True,
    )
    live_spectators = models.PositiveIntegerField(
        verbose_name=_("spectateurs"),
        blank=True,
        null=True,
        default=None,
    )

    def __str__(self):
        return self.name

    @property
    def twitch_url(self):
        return f"https://twitch.tv/{self.twitch_login}"

    @staticmethod
    def _download_and_store_image(url, field):
        if not url:
            return

        res_image = requests.get(url)
        if not res_image.ok:
            return

        image = BytesIO()
        image.write(res_image.content)
        filename = f"image{os.path.splitext(url)[1]}"
        field.save(filename, files.File(image))

    def update_from_twitch_data(self, twitch_data):
        """
        Updates this instance using the data returned by Twitch. Does not save
        the instance.

        :param twitch_data: The Twitch data: https://dev.twitch.tv/docs/api/reference#get-users
        """
        self.name = twitch_data["display_name"]

        self.twitch_id = twitch_data["id"]
        self.twitch_login = twitch_data["login"]

        self.description = twitch_data["description"]

        self._download_and_store_image(twitch_data.get("profile_image_url"), self.profile_image)
        self._download_and_store_image(twitch_data.get("offline_image_url"), self.background_image)

    def update_stream_from_twitch_data(self, twitch_data):
        self.live_title = twitch_data["title"]
        self.live_game_name = twitch_data["game_name"]
        self.live_spectators = twitch_data["viewer_count"]

        thumbnail = (
            twitch_data["thumbnail_url"]
            .replace("{width}", str(settings.POG_PREVIEWS["WIDTH"]))
            .replace("{height}", str(settings.POG_PREVIEWS["HEIGHT"]))
        )

        self._download_and_store_image(thumbnail, self.live_preview)


class EventSubSubscription(models.Model):
    class Meta:
        verbose_name = _("abonnement EventSub")
        verbose_name_plural = _("abonnements EventSub")

    UNSUBSCRIBED = "unsubscribed"
    SUBSCRIBED = "subscribed"
    PENDING = "pending"
    STATUS_CHOICES = [
        (UNSUBSCRIBED, _("Non-souscrit")),
        (PENDING, _("En attente")),
        (SUBSCRIBED, _("Souscrit")),
    ]

    streamer = models.ForeignKey(
        Streamer,
        verbose_name=_("Streamer"),
        related_name="eventsub_subscriptions",
        on_delete=models.CASCADE,
    )

    type = models.CharField(
        verbose_name=_("subscription type"),
        max_length=100,
    )

    uuid = models.UUIDField(
        verbose_name=_("subscription UUID"),
    )

    secret = models.CharField(
        verbose_name=_("subscription secret"),
        help_text=_("Secret to authenticate the subscription requests from Twitch"),
        max_length=100,
    )

    status = models.CharField(
        verbose_name=_("subscription status"),
        max_length=12,
        choices=STATUS_CHOICES,
        default=UNSUBSCRIBED,
    )

    last_seen = models.DateTimeField(
        verbose_name=_("last seen"),
        help_text=_("When was the last request from Twitch received"),
        blank=True,
        null=True,
    )

    @property
    def last_seen_since(self) -> timedelta:
        return timezone.now() - self.last_seen

    def __str__(self):
        return f"EventSub subscription {self.type}"


class ScheduledStream(models.Model):
    """
    A streamer's planned stream, loaded from Twitch or Google Calendar.
    """

    class Meta:
        verbose_name = _("Stream planifié")
        verbose_name_plural = _("Streams planifiés")

    streamer = models.ForeignKey(
        Streamer,
        verbose_name=_("streamer ayant programmé le stream"),
        related_name="schedule",
        on_delete=models.CASCADE,
    )

    title = models.CharField(_("titre du stream programmé"), max_length=140)

    start = models.DateTimeField(_("heure de début prévue"))
    end = models.DateTimeField(_("heure de fin prévue"))

    category = models.CharField(_("catégorie du stream"), max_length=140, blank=True, null=True)

    weekly = models.BooleanField(_("hebdomadaire ?"))

    twitch_segment_id = models.CharField(
        _("identifiant interne du segment Twitch"),
        max_length=128,
        null=True,
        blank=True,
        editable=False,
    )

    google_calendar_event_id = models.CharField(
        _("identifiant interne de l'événement Google Calendar"), max_length=128, null=True, blank=True, editable=False
    )

    @property
    @admin.display(description=_("Durée"))
    def duration(self):
        return self.end - self.start

    @property
    def now(self):
        now = timezone.now()
        return self.start < now < self.end

    def __str__(self):
        return f"{self.title} ({self.streamer}, {self.start} → {self.end})"
