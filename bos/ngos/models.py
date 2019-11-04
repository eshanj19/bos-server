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

from bos.constants import PUBLIC_KEY_LENGTH_NGO


def generate_ngo_key():
    return get_random_string(PUBLIC_KEY_LENGTH_NGO)


class NGO(models.Model):
    key = models.CharField(max_length=PUBLIC_KEY_LENGTH_NGO, default=generate_ngo_key, unique=True)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    logo = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ngos'

    def __str__(self):
        return self.name


class NGORegistrationResource(models.Model):
    NGO = 'ngo'
    COACH = 'coach'
    ATHLETE = 'athlete'
    REGISTRATION_TYPES = (
        (NGO, 'ngo'),
        (COACH, 'coach'),
        (ATHLETE, 'athlete'),
    )

    type = models.CharField(choices=REGISTRATION_TYPES, max_length=50, null=False, blank=False)
    resource = models.ForeignKey('resources.Resource', null=False, blank=False, on_delete=models.PROTECT)
    ngo = models.ForeignKey('ngos.NGO', null=False, blank=False, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ngo_registration_resource'
        unique_together = ('ngo', 'type')

    def __str__(self):
        return self.label
