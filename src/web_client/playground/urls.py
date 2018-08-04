from django.urls import path

from .views import *

app_name = "playground"
urlpatterns = [
    # path("", view=user_list_view, name="list"),
    path("demo-1/", view=Demo1View.as_view(), name="demo1"),
    path("demo-2/", view=Demo2View.as_view(), name="demo2"),
    path("demo-3/", view=Demo3View.as_view(), name="demo3"),
    path("demo-4/", view=Demo4View.as_view(), name="demo4"),

]
