from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('professions/', views.professions, name='professions'),
    path('profession/<slug:slug>/', views.profession_detail, name='profession_detail'),
    path('profession/<slug:slug>/<str:pricing>/', views.profession_detail, name='profession_detail_filtered'),
    path('tool/<slug:slug>/', views.tool_detail, name='tool_detail'),
    path('stacks/', views.stacks, name='stacks'),
    path('stack/<slug:slug>/', views.stack_detail, name='stack_detail'),
    path('search/', views.search, name='search'),
    path('my-stacks/', views.my_stacks, name='my_stacks'),
    path('ai-builder/', views.ai_stack_builder, name='ai_stack_builder'),
    path('api/ai-generate-tools/', views.ai_generate_tools, name='ai_generate_tools'),
    path('api/create-custom-stack/', views.create_custom_stack, name='create_custom_stack'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
