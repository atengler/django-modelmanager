from django.conf.urls import url

from .views import LoginView


app_name = 'identity'
urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
]
