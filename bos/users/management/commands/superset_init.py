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

from django.core.management import BaseCommand
from django.db import connection

from ngos.models import NGO
from bos.create_view_as import create_view_as
from django.db.models import F, CharField
from django.db.models import Value
from django.db.models.functions import Concat

from users.management.commands.superset_api import SUPERSET_BASE_TABLE_NAME
from users.models import UserReading


def _superset_init():
    with connection.cursor() as cursor:
        ngos = NGO.objects.all().values_list("key", flat=True)

        # /Drop temporary tables in case the process got cut off before
        for ngo in ngos:
            print(ngo)
            view_name = SUPERSET_BASE_TABLE_NAME % (ngo)

            drop_view_string = "DROP VIEW IF EXISTS %s" % view_name
            cursor.execute(
                drop_view_string
            )
            # Create the new table from the summary query
            ngo_filter = {
                'ngo__key': ngo,
                'is_active': True
            }

            user_readings = UserReading.objects.filter(**ngo_filter).annotate(
                user_full_name=Concat('user__first_name',
                                      Value(' '),
                                      'user__middle_name',
                                      Value(' '),
                                      'user__last_name', output_field=CharField()),
                measurement_label=F('measurement__label'),
                user_gender=F('user__gender'),
                user_is_active=F('user__is_active'),
            ).values_list(
                'key',
                'measurement_label',
                'value',
                'user_full_name',
                'user_gender',
                'user_is_active',
                'creation_time',
                'last_modification_time',
            )
            create_view_string = view_name
            create_view_as(
                create_view_string,
                user_readings,
            )


class Command(BaseCommand):
    help = 'Create views for superset'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        _superset_init()
        print("Finished")
        return
