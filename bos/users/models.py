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

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _

from bos.constants import PUBLIC_KEY_LENGTH_USER, LENGTH_TOKEN, LENGTH_RESET_PASSWORD_TOKEN, FIELD_LENGTH_NAME, \
    LENGTH_USERNAME, PUBLIC_KEY_LENGTH_USER_READING
from bos.permissions import PERMISSION_BOS_ADMIN


def generate_user_key():
    return get_random_string(PUBLIC_KEY_LENGTH_USER)


def generate_user_reading_key():
    return get_random_string(PUBLIC_KEY_LENGTH_USER_READING)


def generate_user_auth_token():
    return get_random_string(LENGTH_TOKEN)


def generate_user_reset_token():
    return get_random_string(LENGTH_RESET_PASSWORD_TOKEN)


def generate_username():
    return get_random_string(LENGTH_USERNAME)


class User(AbstractUser):
    ENGLISH = 'en_IN'
    HINDI = 'hi_IN'
    KANNADA = 'ka_IN'
    LANGUAGES = (
        (ENGLISH, 'English'),
        (HINDI, 'Hindi'),
        (KANNADA, 'Kannada')
    )
    ADMIN = 'admin'
    ATHLETE = 'athlete'
    COACH = 'coach'
    ROLES = (
        (ADMIN, 'admin'),
        (ATHLETE, 'athlete'),
        (COACH, 'coach')
    )

    key = models.CharField(max_length=PUBLIC_KEY_LENGTH_USER, default=generate_user_key, unique=True)
    first_name = models.CharField(max_length=FIELD_LENGTH_NAME, null=False, blank=False)
    middle_name = models.CharField(max_length=FIELD_LENGTH_NAME, null=True, blank=True)
    last_name = models.CharField(max_length=FIELD_LENGTH_NAME, null=False, blank=False)
    ngo = models.ForeignKey('ngos.NGO', null=True, blank=True, on_delete=models.PROTECT)
    email = models.CharField(max_length=255,
                             unique=True,
                             null=True,
                             blank=True,
                             error_messages={
                                 'unique': _("user with this email already exists."),
                             })
    password = models.CharField(max_length=1024, null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, null=False, blank=False)
    language = models.CharField(max_length=5, choices=LANGUAGES, default=ENGLISH, null=False, blank=True)
    reset_password = models.BooleanField(default=True)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return ''.join(
            [self.first_name, ' ', self.middle_name, ' ', self.last_name])

    class Meta:
        db_table = 'users'
        permissions = (
            PERMISSION_BOS_ADMIN[0:2],
        )


class MobileAuthToken(models.Model):
    token = models.CharField(max_length=LENGTH_TOKEN, default=generate_user_auth_token, unique=True)
    user = models.ForeignKey('users.User', null=True, blank=False, on_delete=models.PROTECT)
    expiry_date = models.DateTimeField(null=False, blank=False)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mobile_auth_tokens'


class UserReading(models.Model):
    key = models.CharField(max_length=PUBLIC_KEY_LENGTH_USER_READING, default=generate_user_reading_key, unique=True)
    user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT, related_name="user")
    ngo = models.ForeignKey('ngos.NGO', null=False, blank=False, on_delete=models.PROTECT)
    by_user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT, related_name='user_by')
    entered_by = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT,
                                   related_name='entered_by')
    measurement = models.ForeignKey('measurements.Measurement', null=False, blank=False, on_delete=models.PROTECT)
    user_resource_template = models.ForeignKey('users.UserTemplate', related_name='template', null=True, blank=True,
                                               on_delete=models.PROTECT)
    user_resource_template_session = models.ForeignKey('users.UserTemplate', related_name='session_template', null=True,
                                                       blank=True, on_delete=models.PROTECT)
    resource_template_session_uuid = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    value = models.CharField(max_length=50, null=False, blank=False)
    is_active = models.BooleanField(default=True, null=False, blank=True)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_readings'


class UserHierarchy(models.Model):
    parent_user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT,
                                    related_name="parent_user")
    child_user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT,
                                   related_name="child_user")
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_hierarchy'


class UserResetPassword(models.Model):
    user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT)
    reset_password_token = models.CharField(max_length=LENGTH_RESET_PASSWORD_TOKEN, default=generate_user_reset_token,
                                            unique=True)
    is_used = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    expiry_date = models.DateTimeField(null=False)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_reset_password'


class UserTemplate(models.Model):
    user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT)
    resource_template = models.ForeignKey('ngos.ResourceTemplate', null=False, blank=False, on_delete=models.PROTECT)
    data = JSONField()
    is_active = models.BooleanField(default=True, blank=True)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_templates'


class UserFile(models.Model):
    user = models.ForeignKey('users.User', null=False, blank=False, on_delete=models.PROTECT)
    resource_file = models.ForeignKey('ngos.ResourceFile', null=False, blank=False, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True, blank=True)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_files'
        unique_together = ('user', 'resource_file')
