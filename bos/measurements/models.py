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
from bos.constants import PUBLIC_KEY_LENGTH_MEASUREMENT, PUBLIC_KEY_LENGTH_MEASUREMENT_TYPE


def generate_measurement_key():
    return get_random_string(PUBLIC_KEY_LENGTH_MEASUREMENT)


class Measurement(models.Model):
    TEXT = 'text'
    NUMERIC = 'numeric'
    BOOLEAN = 'boolean'
    MEASUREMENT_INPUT_TYPES = (
        (TEXT, 'text'),
        (NUMERIC, 'numeric'),
        (BOOLEAN, 'boolean'),
    )

    key = models.CharField(max_length=PUBLIC_KEY_LENGTH_MEASUREMENT, default=generate_measurement_key, unique=True)
    label = models.CharField(max_length=50, null=False, blank=False)
    types = models.ManyToManyField('measurements.MeasurementType', blank=False)
    input_type = models.CharField(choices=MEASUREMENT_INPUT_TYPES, max_length=50, null=False, blank=False)
    uom = models.CharField(max_length=50, null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True, blank=True)
    ngo = models.ForeignKey('ngos.NGO', null=False, blank=False, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'measurements'

    def __str__(self):
        return self.label


class MeasurementType(models.Model):
    key = models.CharField(max_length=PUBLIC_KEY_LENGTH_MEASUREMENT_TYPE, default=generate_measurement_key, unique=True)
    label = models.CharField(max_length=50, null=False, blank=False)
    is_active = models.BooleanField(default=True, blank=True)
    ngo = models.ForeignKey('ngos.NGO', null=False, blank=False, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'measurement_types'

    def __str__(self):
        return self.label
