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

from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.postgres.fields import JSONField

from bos.permissions import PERMISSION_CAN_ADD_FILE, PERMISSION_CAN_CHANGE_FILE, PERMISSION_CAN_DESTROY_FILE, \
    PERMISSION_CAN_VIEW_FILE, PERMISSION_CAN_ADD_CURRICULUM, PERMISSION_CAN_CHANGE_CURRICULUM, \
    PERMISSION_CAN_DESTROY_CURRICULUM, PERMISSION_CAN_VIEW_CURRICULUM, PERMISSION_CAN_ADD_TRAINING_SESSION, \
    PERMISSION_CAN_CHANGE_TRAINING_SESSION, PERMISSION_CAN_DESTROY_TRAINING_SESSION, \
    PERMISSION_CAN_VIEW_TRAINING_SESSION, PERMISSION_CAN_DESTROY_REGISTRATION_FORM, \
    PERMISSION_CAN_VIEW_REGISTRATION_FORM, PERMISSION_CAN_CHANGE_REGISTRATION_FORM, PERMISSION_CAN_ADD_REGISTRATION_FORM


def generate_resource_key():
    return get_random_string(PUBLIC_KEY_LENGTH_RESOURCE)


from bos.constants import PUBLIC_KEY_LENGTH_RESOURCE, LENGTH_LABEL, LENGTH_DESCRIPTION


# Should resources label be language specific?

class Resource(models.Model):
    CURRICULUM = 'curriculum'
    TRAINING_SESSION = 'session'
    REGISTRATION_FORM = 'registration'
    BENCHMARK = 'benchmark'
    FILE = 'file'
    RESOURCE_TEMPLATE_TYPES = (
        (CURRICULUM, 'Curriculum'),
        (TRAINING_SESSION, 'Session'),
        (REGISTRATION_FORM, 'Registration'),
        (BENCHMARK, 'Benchmark'),
        (FILE, 'File'),
    )

    key = models.CharField(max_length=PUBLIC_KEY_LENGTH_RESOURCE, default=generate_resource_key, unique=True)
    data = JSONField()
    label = models.CharField(max_length=LENGTH_LABEL, null=False, blank=False)
    description = models.CharField(max_length=LENGTH_DESCRIPTION, null=True, blank=True)
    type = models.CharField(choices=RESOURCE_TEMPLATE_TYPES, max_length=50, null=False, blank=False)
    is_active = models.BooleanField(default=True, blank=True)
    is_shared = models.BooleanField(default=True, blank=True)
    ngo = models.ForeignKey('ngos.NGO', null=False, blank=False, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resources'
        permissions = (
            PERMISSION_CAN_ADD_TRAINING_SESSION[0:2],
            PERMISSION_CAN_CHANGE_TRAINING_SESSION[0:2],
            PERMISSION_CAN_DESTROY_TRAINING_SESSION[0:2],
            PERMISSION_CAN_VIEW_TRAINING_SESSION[0:2],
            PERMISSION_CAN_ADD_FILE[0:2],
            PERMISSION_CAN_CHANGE_FILE[0:2],
            PERMISSION_CAN_DESTROY_FILE[0:2],
            PERMISSION_CAN_VIEW_FILE[0:2],
            PERMISSION_CAN_ADD_CURRICULUM[0:2],
            PERMISSION_CAN_CHANGE_CURRICULUM[0:2],
            PERMISSION_CAN_DESTROY_CURRICULUM[0:2],
            PERMISSION_CAN_VIEW_CURRICULUM[0:2],
            PERMISSION_CAN_ADD_REGISTRATION_FORM[0:2],
            PERMISSION_CAN_CHANGE_REGISTRATION_FORM[0:2],
            PERMISSION_CAN_DESTROY_REGISTRATION_FORM[0:2],
            PERMISSION_CAN_VIEW_REGISTRATION_FORM[0:2],
        )

    def __str__(self):
        return self.label

