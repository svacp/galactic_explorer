"""galactic_explorer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from portal import views

urlpatterns = [
    path(
        '',
        views.view_index, name='home'),
    path(
        'collections/',
        views.view_collections, name='collections'),
    path(
        'collections/<str:collection_id>/',
        views.view_collection_detail, name='collection_detail'),
    path(
        'collections/<str:collection_id>/stats/',
        views.view_collection_stats, name='collection_stats'),
]
