from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class Demo1View(TemplateView):
    template_name = "playground/interact_demo_1.html"


class Demo2View(TemplateView):
    template_name = "playground/interact_demo_2.html"


class Demo3View(TemplateView):
    template_name = "playground/interact_demo_3.html"


class Demo4View(TemplateView):
    template_name = "playground/interact_demo_4.html"
