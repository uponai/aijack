from django.urls import path
from .views import BlogListView, BlogDetailView, admin_blogs, admin_blog_create, admin_blog_edit

urlpatterns = [
    path('admin/', admin_blogs, name='admin_blogs'),
    path('admin/create/', admin_blog_create, name='admin_blog_create'),
    path('admin/<int:pk>/edit/', admin_blog_edit, name='admin_blog_edit'),
    path('', BlogListView.as_view(), name='blog_list'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
]
