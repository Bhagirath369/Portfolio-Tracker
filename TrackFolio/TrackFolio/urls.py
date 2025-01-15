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
    path("", views.signup, name = "signup"),
    path("login/", views.login, name = "login"),
    path("home/", views.home, name = "home"),
    path('add/', views.add_portfolio, name='add_portfolio'),
    path('portfolios/',views.portfolio, name = 'portfolio'),
    path('portfolios/<int:portfolio_id>/', views.portfolio, name='portfolio'),
    path('portfolios/<int:portfolio_id>/delete/', views.delete_portfolio, name='delete_portfolio'),
    
    # path('add/', views.add_portfolio, name='add_portfolio'),
    # path('delete<int:portfolio_id>/', views.delete_portfolio, name='delete_portfolio'),

]
