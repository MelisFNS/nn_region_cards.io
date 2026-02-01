from django.urls import path
from .views import (
    CityListView, CityDetailView,
    city_create, city_edit, city_delete,
    signup, CustomLoginView, CustomLogoutView
)

urlpatterns = [
    path("", CityListView.as_view(), name="city_list"),

    # add/edit/delete ДО detail
    path("city/add/", city_create, name="city_add"),
    path("city/<str:slug>/edit/", city_edit, name="city_edit"),
    path("city/<str:slug>/delete/", city_delete, name="city_delete"),
    path("city/<str:slug>/", CityDetailView.as_view(), name="city_detail"),

    path("signup/", signup, name="signup"),
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", CustomLogoutView.as_view(), name="logout"),
]
