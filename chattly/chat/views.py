from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class HomeView(TemplateView):
    http_method_names = ["get"]
    template_name = "chat/main.html"
