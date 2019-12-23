from datetime import datetime
from django.utils.timezone import make_aware

from rest_framework import authentication

from users.models import MobileAuthToken


class MobileAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for validating tokens sent from android apps.
    Check http://www.django-rest-framework.org/api-guide/authentication/#custom-authentication
    for details
    """

    def authenticate(self, request):
        token_header = request.META.get('HTTP_AUTHORIZATION', None)
        try:
            token = token_header.split(' ')[1]
        except Exception:
            return None, None

        if token:
            auth_token = MobileAuthToken.objects.filter(token=token, expiry_date__gt=make_aware(datetime.now())).first()
            if auth_token:
                # print("Token exists")
                return auth_token.user, None
            # else:
                # print("Auth Token not found")
        # else:
        #     print("Token in header missing")
        return None, None
