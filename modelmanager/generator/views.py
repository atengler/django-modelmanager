import logging

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from modelmanager.mixins import LoginRequired

from .forms import ContactForm1, ContactForm2
from .generic_views import GeneratedWizardView

LOG = logging.getLogger(__name__)


class OverviewView(LoginRequired, TemplateView):
    template_name = 'generator/overview.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(OverviewView, self).get_context_data(*args, **kwargs)

        return ctx


class GenerateMetadataWizard(GeneratedWizardView):
    initial_dict = {
        'contact_form_1': {
            'subject': 'test',
            'sender': 'test@test.cz'
        }
    }
    template_name = 'common/wizard_form.html'

    def done(self, form_list, **kwargs):
        LOG.error('CONTACT WIZARD DONE')
        return HttpResponseRedirect(reverse_lazy('generator:overview'))
