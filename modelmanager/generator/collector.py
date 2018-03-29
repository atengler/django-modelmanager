from django.conf import settings
from django.core import exceptions as django_exc
from django.core.cache import cache

import logging
import requests

LOG = logging.getLogger(__name__)


class ContextTemplateCollector(object):
    '''
    TODO: document this class
    '''
    url = None
    path = None
    remote = None
    username = None
    password = None
    token = None
    collectors = {
        'github': self._github_collector
        'http': self._http_collector
        'localfs': self._localfs_collector
    }

    def __init__(self, *args, **kwargs):
        default_url = getattr(settings, 'COOKIECUTTER_CONTEXT_URL', None)
        default_path = getattr(settings, 'COOKIECUTTER_CONTEXT_PATH', None)
        default_remote = getattr(settings, 'COOKIECUTTER_CONTEXT_REMOTE', None)
        default_username = getattr(settings, 'COOKIECUTTER_CONTEXT_USERNAME', None)
        default_password = getattr(settings, 'COOKIECUTTER_CONTEXT_PASSWORD', None)
        default_token = getattr(settings, 'COOKIECUTTER_CONTEXT_TOKEN', None)

        self.url = kwargs.get('url', default_url)
        self.path = kwargs.get('path', default_path)
        self.remote = kwargs.get('remote', default_remote)
        self.username = kwargs.get('username', default_username)
        self.password = kwargs.get('password', default_password)
        self.token = kwargs.get('token', default_token)

    def _github_collector(self):
        s = requests.Session()
        url = self.url
        token = self.token

        cached_ctx = cache.get('workflow_context', None)
        if cached_ctx:
            return cached_ctx

        if not url:
            msg = 'Github repository API URL is required to be set as COOKIECUTTER_CONTEXT_URL with COOKIECUTTER_CONTEXT_REMOTE = "github".'
            raise django_exc.ImproperlyConfigured(msg)

        if not token:
            msg = 'Github API token is required to be set as COOKIECUTTER_CONTEXT_TOKEN with COOKIECUTTER_CONTEXT_REMOTE = "github".'
            raise django_exc.ImproperlyConfigured(msg)

        s.headers.update({'Accept': 'application/vnd.github.v3.raw'})
        s.headers.update({'Authorization': 'token ' + str(token)})
        r = s.get(url)
        if r.status_code >= 300:
            try:
                r_json = json.loads(str(r.text))
                r_text = r_json['message']
            except:
                r_text = r.text
            msg = "Could not get remote file from Github:\nSTATUS CODE: %s\nRESPONSE:\n%s" % (str(r.status_code), r_text)
            LOG.error(msg)
            ctx = ""
        else:
            ctx = r.text

        cache.set('workflow_context', ctx, 3600)

        return ctx

    def _http_collector(self):
        s = requests.Session()
        url = self.url
        username = self.username
        password = self.password

        cached_ctx = cache.get('workflow_context', None)
        if cached_ctx:
            return cached_ctx

        if not url:
            msg = 'HTTP URL is required to be set as COOKIECUTTER_CONTEXT_URL with COOKIECUTTER_CONTEXT_REMOTE = "http".'
            raise django_exc.ImproperlyConfigured(msg)

        if username and password:
            r = s.get(url, auth=(username, password))
        else:
            r = s.get(url)

        if r.status_code >= 300:
            msg = "Could not get remote file from HTTP URL %s:\nSTATUS CODE: %s\nRESPONSE:\n%s" % (url, str(r.status_code), r.text)
            LOG.error(msg)
            ctx = ""
        else:
            ctx = r.text

        cache.set('workflow_context', ctx, 3600)

        return ctx

    def _localfs_collector(self):
        path = self.path

        if not path:
            msg = 'Path to file on local filesystem is required to be set as COOKIECUTTER_CONTEXT_PATH with COOKIECUTTER_CONTEXT_REMOTE = "localfs".'
            raise django_exc.ImproperlyConfigured(msg)

        try:
            with io.open(path, 'r') as file_handle:
                ctx = file_handle.read()
        except Exception as e:
            msg = "Could not read file %s: %s" % (path, repr(e))
            LOG.error(msg)
            ctx = ""

        return ctx

    def collect_template(self):
        if not (self.remote and self.remote in self.collectors):
            msg = 'Remote {} is not supported. Supported remotes: {}'.format(str(self.remote), str(self.collectors.keys()))
            raise django_exc.ImproperlyConfigured(msg)

        collector = self.collectors[self.remote]
        return collector()
