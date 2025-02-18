from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from users.views  import *

urlpatterns = [
    path('', include('users.urls')),
    path('admin/', admin.site.urls),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register'),
    path('logout/', user_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)