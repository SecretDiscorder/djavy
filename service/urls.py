from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    # Examples:
    # url(r'^$', 'djandro.views.home', name='home'),
#    url(r'^myapp/', include('myapp.urls')),
    path('', include('tool.urls'), name=""),
    path('admin/', admin.site.urls),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
