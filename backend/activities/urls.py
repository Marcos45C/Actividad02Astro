# from django.urls import path

# from . import views

# app_name = "activities"


# urlpatterns = [
#     path("", views.activity_list, name="list"),
#     path("api/v1/activities/", views.activity_api_list, name="api-list"),

#     # GET /api/v1/activities/{activity_id}
#     path("api/v1/activities/<uuid:id>/", views.activity_api_detail, name="api-detail"),

#     # GET /api/v1/me/enrollments
#     path("api/v1/me/enrollments/", views.activity_api_enrollments, name="api-enrollments"),

#     # PUT /api/v1/me/enrollments/{activity_id}
#     # DELETE /api/v1/me/enrollments/{activity_id}
#     path(
#         "api/v1/me/enrollments/<uuid:activity_id>/",
#         views.EnrollmentDetailView.as_view(),
#         name="api-enrollment-detail",
#     ),
# ]

from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
]