from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('professions/', views.professions, name='professions'),
    path('profession/<slug:slug>/', views.profession_detail, name='profession_detail'),
    path('tool/<slug:slug>/', views.tool_detail, name='tool_detail'),
    path('stacks/', views.stacks, name='stacks'),
    path('stack/<slug:slug>/', views.stack_detail, name='stack_detail'),
    path('search/', views.search, name='search'),
]
