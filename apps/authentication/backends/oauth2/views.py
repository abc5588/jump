from django.views import View
from django.contrib import auth
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from authentication.utils import build_absolute_uri
from common.utils import get_logger

logger = get_logger(__file__)


class OAuth2AuthRequestView(View):

    def get(self, request):
        log_prompt = "Process OAuth2 GET requests: {}"
        logger.debug(log_prompt.format('Start'))

        base_url = settings.AUTH_OAUTH2_PROVIDER_AUTHORIZATION_ENDPOINT
        query_dict = {
            'client_id': settings.AUTH_OAUTH2_CLIENT_ID, 'response_type': 'code',
            'scope': settings.AUTH_OAUTH2_SCOPE,
            'redirect_uri': build_absolute_uri(
                request, path=reverse(settings.AUTH_OAUTH2_AUTH_LOGIN_CALLBACK_URL_NAME)
            )
        }

        redirect_url = '{url}?{query}'.format(url=base_url, query=urlencode(query_dict))
        logger.debug(log_prompt.format('Redirect login url'))
        return HttpResponseRedirect(redirect_url)


class OAUTH2AuthCallbackView(View):
    http_method_names = ['get', ]

    def get(self, request):
        """ Processes GET requests. """
        log_prompt = "Process GET requests [OAUTH2AuthCallbackView]: {}"
        logger.debug(log_prompt.format('Start'))
        callback_params = request.GET

        if 'code' in callback_params:
            logger.debug(log_prompt.format('Process authenticate'))
            user = auth.authenticate(code=callback_params['code'], request=request)
            if user and user.is_valid:
                logger.debug(log_prompt.format('Login: {}'.format(user)))
                auth.login(self.request, user)
                logger.debug(log_prompt.format('Redirect'))
                return HttpResponseRedirect(
                    settings.AUTH_OAUTH2_AUTHENTICATION_REDIRECT_URI
                )

        logger.debug(log_prompt.format('Redirect'))
        return HttpResponseRedirect(settings.AUTH_OAUTH2_AUTHENTICATION_FAILURE_REDIRECT_URI)
