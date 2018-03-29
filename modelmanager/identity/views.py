import logging

from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import LoginForm

LOG = logging.getLogger(__name__)


class LoginView(FormView):
    template_name = 'identity/login.html'
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next', None)
        if next_url:
           return "%s" % (next_url)
        else:
           return reverse_lazy('index')

    def form_valid(self, form):
        user = None
        username = form.cleaned_data.get('username', None)
        password = form.cleaned_data.get('password', None)

        if username and password:
            user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)

        return super(LoginView, self).form_valid(form)
