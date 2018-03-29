from django.conf.urls import url

from .views import OverviewView, GenerateMetadataWizard


app_name = 'generator'
urlpatterns = [
    url(r'^$', OverviewView.as_view(), name='overview'),
    url(r'^generate/$', GenerateMetadataWizard.as_view(), name='generate')
]
