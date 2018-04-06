from collections import OrderedDict
from django import forms
from django.forms import formsets
from formtools.wizard.storage.exceptions import NoFileStorageConfigured
from formtools.wizard.views import SessionWizardView

from .forms import ContactForm1, ContactForm2

import six


class GeneratedWizardView(SessionWizardView):

    @classmethod
    def get_initkwargs(cls, form_list=[], initial_dict=None, instance_dict=None,
                       condition_dict=None, *args, **kwargs):
        """
        Creates a dict with all needed parameters for the form wizard instances
        * `form_list` - is a list of forms. The list entries can be single form
          classes or tuples of (`step_name`, `form_class`). If you pass a list
          of forms, the wizardview will convert the class list to
          (`zero_based_counter`, `form_class`). This is needed to access the
          form for a specific step.
        * `initial_dict` - contains a dictionary of initial data dictionaries.
          The key should be equal to the `step_name` in the `form_list` (or
          the str of the zero based counter - if no step_names added in the
          `form_list`)
        * `instance_dict` - contains a dictionary whose values are model
          instances if the step is based on a ``ModelForm`` and querysets if
          the step is based on a ``ModelFormSet``. The key should be equal to
          the `step_name` in the `form_list`. Same rules as for `initial_dict`
          apply.
        * `condition_dict` - contains a dictionary of boolean values or
          callables. If the value of for a specific `step_name` is callable it
          will be called with the wizardview instance as the only argument.
          If the return value is true, the step's form will be used.

        Override: we expect empty form_list here so we can construct it later,
        form_list computing part is moved to `set_form_list` for this reason.
        """
        kwargs.update({
            'form_list': form_list,
            'initial_dict': (
                initial_dict or
                kwargs.pop('initial_dict', getattr(cls, 'initial_dict', None)) or {}
            ),
            'instance_dict': (
                instance_dict or
                kwargs.pop('instance_dict', getattr(cls, 'instance_dict', None)) or {}
            ),
            'condition_dict': (
                condition_dict or
                kwargs.pop('condition_dict', getattr(cls, 'condition_dict', None)) or {}
            )
        })
        return kwargs

    def set_form_list(self, form_list):
        """
        Creates computed_form_list from the original form_list.
        Separated from the original `set_initkwargs` method.
        """
        computed_form_list = OrderedDict()

        # walk through the passed form list
        for i, form in enumerate(form_list):
            if isinstance(form, (list, tuple)):
                # if the element is a tuple, add the tuple to the new created
                # sorted dictionary.
                computed_form_list[six.text_type(form[0])] = form[1]
            else:
                # if not, add the form with a zero based counter as unicode
                computed_form_list[six.text_type(i)] = form

        # walk through the new created list of forms
        for form in six.itervalues(computed_form_list):
            if issubclass(form, formsets.BaseFormSet):
                # if the element is based on BaseFormSet (FormSet/ModelFormSet)
                # we need to override the form variable.
                form = form.form
            # check if any form contains a FileField, if yes, we need a
            # file_storage added to the wizardview (by subclassing).
            for field in six.itervalues(form.base_fields):
                if (isinstance(field, forms.FileField) and
                        not hasattr(cls, 'file_storage')):
                    raise NoFileStorageConfigured(
                        "You need to define 'file_storage' in your "
                        "wizard view in order to handle file uploads."
                    )

        self.form_list = computed_form_list

    def dispatch(self, request, *args, **kwargs):
        """
        This method gets called by the routing engine. The first argument is
        `request` which contains a `HttpRequest` instance.
        The request is stored in `self.request` for later use. The storage
        instance is stored in `self.storage`.
        After processing the request using the `dispatch` method, the
        response gets updated by the storage engine (for example add cookies).

        Override: construct `form_list` here and save it on view instance
        """
        form_list = [('contact_form_1', ContactForm1), ('contact_form_2', ContactForm2)]
        self.set_form_list(form_list)
        return super(GeneratedWizardView, self).dispatch(request, *args, **kwargs)
