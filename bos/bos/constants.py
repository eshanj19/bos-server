#  Copyright (c) 2019 Maverick Labs
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as,
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from enum import Enum

from django.utils.translation import gettext as _

PUBLIC_KEY_LENGTH_NGO = 10
PUBLIC_KEY_LENGTH_MEASUREMENT = 10
PUBLIC_KEY_LENGTH_MEASUREMENT_TYPE = 10
PUBLIC_KEY_LENGTH_USER = 10
PUBLIC_KEY_LENGTH_USER_REQUEST = 10
PUBLIC_KEY_LENGTH_USER_READING = 10
PUBLIC_KEY_LENGTH_USER_GROUP = 10
PUBLIC_KEY_LENGTH_ATHLETE = 10
PUBLIC_KEY_LENGTH_RESOURCE = 10

LENGTH_TOKEN = 20
LENGTH_LABEL = 500
LENGTH_DESCRIPTION = 2000
LENGTH_NOTE_FIELD = 500
LENGTH_RESET_PASSWORD_TOKEN = 10
LENGTH_USERNAME = 10
FIELD_LENGTH_NAME = 50
API_URL = 'http://192.168.0.2/reset_password/'
METHOD_POST = 'POST'
METHOD_GET = 'GET'
MESSAGE_KEY = 'message'


class DisableCSRFMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response


class GroupType(Enum):
    ADMIN = 'admin'
    COACH = 'coach'
    ATHLETE = 'athlete'


DEFAULT_ROLES = [GroupType.ADMIN.value, GroupType.COACH.value, GroupType.ATHLETE.value]
VALID_FILE_EXTENSIONS = ['.png', '.jpeg', '.jpg', 'txt', 'mp4', 'mp3', '.pdf']
