from django.urls import path, include, re_path

urlpatterns = [
    # Examples:
    # url(r'^$', 'djandro.views.home', name='home'),
    re_path('', include('tool.urls')),
]
