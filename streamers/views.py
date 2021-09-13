from django.views.generic import TemplateView

from streamers.models import Streamer


class HomeView(TemplateView):
    template_name = "home.html"
    extra_context = {
        "streamers": Streamer.objects.all(),
        "live_streamers": list(Streamer.objects.filter(live=True))
    }
