from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tools/', views.browse_tools, name='browse_tools'),
    path('guide/', views.guide, name='guide'),
    path('submit-tool/', views.submit_tool, name='submit_tool'),
    path('api/browse-tools/', views.browse_tools_api, name='browse_tools_api'),
    path('professions/', views.professions, name='professions'),
    path('profession/<slug:slug>/', views.profession_detail, name='profession_detail'),
    path('profession/<slug:slug>/<str:pricing>/', views.profession_detail, name='profession_detail_filtered'),
    path('tool/<slug:slug>/report/', views.report_tool, name='report_tool'),
    path('tool/<slug:slug>/', views.tool_detail, name='tool_detail'),
    path('visit/<slug:slug>/', views.visit_tool, name='visit_tool'),
    path('stacks/', views.stacks, name='stacks'),
    path('stack/<slug:slug>/', views.stack_detail, name='stack_detail'),
    path('search/', views.search, name='search'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('my-stacks/', views.my_stacks, name='my_stacks'),
    path('stack/<slug:slug>/edit/', views.edit_custom_stack, name='edit_custom_stack'),
    path('stack/<slug:slug>/delete/', views.delete_custom_stack, name='delete_custom_stack'),
    path('ai-builder/', views.ai_stack_builder, name='ai_stack_builder'),
    path('api/ai-generate-tools/', views.ai_generate_tools, name='ai_generate_tools'),
    path('api/create-custom-stack/', views.create_custom_stack, name='create_custom_stack'),
    path('api/save-tool/<int:tool_id>/', views.toggle_save_tool, name='toggle_save_tool'),
    path('api/save-stack/<slug:stack_slug>/', views.toggle_save_stack, name='toggle_save_stack'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Tool Management
    path('admin-dashboard/tools/', views.admin_tools, name='admin_tools'),
    path('admin-dashboard/tools/add/', views.admin_tool_create, name='admin_tool_create'),
    path('admin-dashboard/tools/<slug:slug>/edit/', views.admin_tool_edit, name='admin_tool_edit'),
    path('admin-dashboard/tools/<slug:slug>/delete/', views.admin_tool_delete, name='admin_tool_delete'),

    # Stack Management
    path('admin-dashboard/stacks/', views.admin_stacks, name='admin_stacks'),
    path('admin-dashboard/stacks/add/', views.admin_stack_create, name='admin_stack_create'),
    path('admin-dashboard/stacks/<slug:slug>/edit/', views.admin_stack_edit, name='admin_stack_edit'),
    path('admin-dashboard/stacks/<slug:slug>/delete/', views.admin_stack_delete, name='admin_stack_delete'),

    # Profession Management
    path('admin-dashboard/professions/', views.admin_professions, name='admin_professions'),
    path('admin-dashboard/professions/add/', views.admin_profession_create, name='admin_profession_create'),
    path('admin-dashboard/professions/<slug:slug>/edit/', views.admin_profession_edit, name='admin_profession_edit'),
    path('admin-dashboard/professions/<slug:slug>/delete/', views.admin_profession_delete, name='admin_profession_delete'),

    # Bulk Upload
    path('admin-dashboard/bulk-upload/', views.bulk_upload_tools, name='bulk_upload_tools'),
    path('admin-dashboard/tools/<slug:slug>/ai-complete/', views.ai_complete_tool, name='ai_complete_tool'),
    path('admin-dashboard/stacks/<slug:slug>/ai-complete/', views.ai_complete_stack, name='ai_complete_stack'),
    path('admin-dashboard/professions/<slug:slug>/ai-complete/', views.ai_complete_profession, name='ai_complete_profession'),

    # Legal
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('cookies/', views.CookieView.as_view(), name='cookies'),
    path('api/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    
    # Webcheck
    path('admin-dashboard/webcheck/', views.admin_webcheck, name='admin_webcheck'),
    path('api/webcheck/pending/', views.api_get_pending_webcheck_tools, name='api_get_pending_webcheck_tools'),
    path('api/webcheck/process/<int:tool_id>/', views.api_process_webcheck_tool, name='api_process_webcheck_tool'),
    
    # Notifications API
    path('api/notifications/', views.get_active_notifications, name='get_active_notifications'),
    
    # Admin Notifications
    path('admin-dashboard/notifications/', views.admin_notifications, name='admin_notifications'),
]
