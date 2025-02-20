"""
URL configuration for TrackFolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.contrib import admin
from django.urls import path
from TrackFolio import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name = "home"),
    path("signup/", views.signup, name = "signup"),
    path("login/", views.login, name = "login"),
    path("logout/", views.logout, name = "logout"),
    path("dashboards/", views.dashboard, name = "dashboard"),
    path('add/', views.add_portfolio, name='add_portfolio'),
    path('portfolio/<int:portfolio_id>/', views.portfolio, name='portfolio'),
    path('portfolio/<int:portfolio_id>/delete/', views.delete_portfolio, name='delete_portfolio'),
    path('portfolio/<int:portfolio_id>/add_transaction', views.add_transaction, name='add_transaction'),
    path('portfolio/<int:portfolio_id>/error_display', views.error_display, name = "error_display"),
    path('portfolio/<int:portfolio_id>/<int:transaction_id>/delete_transaction/', views.delete_transaction, name='delete_transaction'),
    path('portfolio/<int:portfolio_id>/<int:transaction_id>/view_transaction/', views.view_transaction, name='view_transaction'),
]
