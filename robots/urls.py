"""
URL patterns for the robots app.
SEO-friendly, clean URL structure.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Public Robot Pages
    path('robots/', views.robots_list, name='robots'),
    path('robot/<slug:slug>/', views.robot_detail, name='robot_detail'),
    
    # Company Pages
    path('robots/companies/', views.robot_companies, name='robot_companies'),
    path('robots/company/<slug:slug>/', views.robot_company_detail, name='robot_company_detail'),
    
    # Special Views
    path('robots/compare/', views.robot_comparison, name='robot_comparison'),
    path('robots/timeline/', views.robot_timeline, name='robot_timeline'),
    path('robots/matrix/', views.robot_matrix, name='robot_matrix'),
    
    # News
    path('robots/news/', views.robot_news_list, name='robot_news'),
    path('robots/news/<slug:slug>/', views.robot_news_detail, name='robot_news_detail'),
    
    # Admin Dashboard (Custom)
    path('admin-dashboard/robots/', views.admin_robots, name='admin_robots'),
    path('admin-dashboard/robots/add/', views.admin_robot_create, name='admin_robot_create'),
    path('admin-dashboard/robots/<slug:slug>/edit/', views.admin_robot_edit, name='admin_robot_edit'),
    path('admin-dashboard/robots/<slug:slug>/delete/', views.admin_robot_delete, name='admin_robot_delete'),
    
    path('admin-dashboard/robot-companies/', views.admin_robot_companies, name='admin_robot_companies'),
    path('admin-dashboard/robot-companies/add/', views.admin_robot_company_create, name='admin_robot_company_create'),
    path('admin-dashboard/robot-companies/<slug:slug>/edit/', views.admin_robot_company_edit, name='admin_robot_company_edit'),
    path('admin-dashboard/robot-companies/<slug:slug>/delete/', views.admin_robot_company_delete, name='admin_robot_company_delete'),
    
    path('admin-dashboard/robot-news/', views.admin_robot_news, name='admin_robot_news'),
    path('admin-dashboard/robot-news/add/', views.admin_robot_news_create, name='admin_robot_news_create'),
    path('admin-dashboard/robot-news/<slug:slug>/edit/', views.admin_robot_news_edit, name='admin_robot_news_edit'),
    path('admin-dashboard/robot-news/<slug:slug>/delete/', views.admin_robot_news_delete, name='admin_robot_news_delete'),
    
    # Bulk Upload
    path('admin-dashboard/bulk-upload-robots/', views.bulk_upload_robots, name='bulk_upload_robots'),
    
    # API Endpoints
    path('api/save-robot/<int:robot_id>/', views.toggle_save_robot, name='toggle_save_robot'),
    path('api/robots/comparison/add/', views.add_to_comparison, name='add_to_comparison'),
    path('api/robots/comparison/remove/', views.remove_from_comparison, name='remove_from_comparison'),
    path('api/robots/comparison/clear/', views.clear_comparison, name='clear_comparison'),
    path('api/robots/comparison/status/', views.robot_comparison_status, name='robot_comparison_status'),
]
