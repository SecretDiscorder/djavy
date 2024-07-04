from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'djandro.views.home', name='home'),
#    url(r'^myapp/', include('myapp.urls')),
    url('', include('tool.urls'), name=""),
    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
