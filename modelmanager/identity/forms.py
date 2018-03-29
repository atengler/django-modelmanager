from django import forms

from django.contrib.auth.forms import AuthenticationForm


class BootstrapFormMixin(object):

    def __init__(self, *args, **kwargs):
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass
