from django.urls import path

from . import views


app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
    path("api/activities/", views.activity_api_list, name="api-list"),
]
