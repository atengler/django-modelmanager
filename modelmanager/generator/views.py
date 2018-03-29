import logging

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from formtools.wizard.views import SessionWizardView
from modelmanager.mixins import LoginRequired

from .forms import ContactForm1, ContactForm2

LOG = logging.getLogger(__name__)


class OverviewView(LoginRequired, TemplateView):
    template_name = 'generator/overview.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(OverviewView, self).get_context_data(*args, **kwargs)

        return ctx


class GenerateMetadataWizard(SessionWizardView):
    form_list = [('contact_form_1', ContactForm1), ('contact_form_2', ContactForm2)]
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
