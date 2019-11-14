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

import logging

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from psycopg2._psycopg import DatabaseError

from bos import utils
from bos.constants import GroupType
from bos.defaults import DEFAULT_MEASUREMENT_TYPES, DEFAULT_NGO, DEFAULT_NGO_ADMIN_EMAIL, DEFAULT_NGO_ADMIN_FIRST_NAME, \
    DEFAULT_NGO_ADMIN_LAST_NAME, DEFAULT_NGO_ADMIN_USERNAME, DEFAULT_STUDENT_BASELINES, \
    DefaultMeasurementType, DEFAULT_STUDENT_PROGRESSIONS, DEFAULT_COACH_BASELINES
from bos.permissions import DEFAULT_PERMISSIONS_ADMIN
from measurements.models import MeasurementType, generate_measurement_key, Measurement
from measurements.serializers import MeasurementTypeSerializer, MeasurementSerializer
from ngos.models import NGO, generate_ngo_key
from ngos.serializers import NGOSerializer
from users.models import User, generate_user_key
from users.serializers import UserSerializer


class Command(BaseCommand):
    help = 'Creates default entities in the database if not created'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                try:
                    bos_ngo = NGO.objects.get(name=DEFAULT_NGO)
                    self.stdout.write(self.style.SUCCESS('BoS NGO "%s" exists in database' % DEFAULT_NGO))
                except NGO.DoesNotExist:
                    ngo_data = {"key": generate_ngo_key(), "name": DEFAULT_NGO,
                                "address": "Temp", "description": "", "logo": "", "is_active": True}

                    serializer = NGOSerializer(data=ngo_data)
                    if serializer.is_valid():
                        bos_ngo = serializer.save()
                    else:
                        self.stdout.write(self.style.ERROR('BoS NGO  "%s" not added to database' % DEFAULT_NGO))
                        self.stdout.write(self.style.ERROR('"%s"' % serializer.errors))

                        raise DatabaseError

                    self.stdout.write(self.style.SUCCESS('BoS NGO "%s" added to database' % DEFAULT_NGO))

                for measurement_type in DEFAULT_MEASUREMENT_TYPES:

                    try:
                        MeasurementType.objects.get(label=measurement_type)
                        self.stdout.write(
                            self.style.SUCCESS('MeasurementType "%s" exists in database' % measurement_type))
                        continue
                    except MeasurementType.DoesNotExist:
                        measurement_type_data = {"key": generate_measurement_key(), "label": measurement_type,
                                                 "ngo": bos_ngo.key, "is_active": True}
                        serializer = MeasurementTypeSerializer(data=measurement_type_data)
                        if serializer.is_valid():
                            serializer.save()
                        else:
                            self.stdout.write(
                                self.style.ERROR('MeasurementType "%s" not added to database' % measurement_type))
                            self.stdout.write(self.style.ERROR('"%s"' % serializer.errors))
                            raise DatabaseError
                        self.stdout.write(
                            self.style.SUCCESS('MeasurementType "%s" added to database' % measurement_type))

                try:
                    bos_admin = User.objects.get(email=DEFAULT_NGO_ADMIN_EMAIL)
                    bos_admin.set_password('admin')
                    bos_admin.save()
                    self.stdout.write(
                        self.style.SUCCESS('BoS NGO admin "%s" exists in database' % DEFAULT_NGO_ADMIN_EMAIL))
                except User.DoesNotExist:
                    bos_admin_data = {"key": generate_user_key(), "username": DEFAULT_NGO_ADMIN_USERNAME,
                                      "first_name": DEFAULT_NGO_ADMIN_FIRST_NAME,
                                      "last_name": DEFAULT_NGO_ADMIN_LAST_NAME, "email": DEFAULT_NGO_ADMIN_EMAIL,
                                      "ngo": bos_ngo.key,
                                      "is_active": True}

                    serializer = UserSerializer(data=bos_admin_data)
                    if serializer.is_valid():
                        bos_admin = serializer.save()
                        bos_admin.set_password('admin')
                        bos_admin.save()
                    else:
                        self.stdout.write(
                            self.style.ERROR('BoS NGO  admin "%s" not added to database' % DEFAULT_NGO_ADMIN_EMAIL))
                        self.stdout.write(self.style.ERROR('"%s"' % serializer.errors))

                        raise DatabaseError

                    self.stdout.write(
                        self.style.SUCCESS('BoS NGO admin "%s" added to database' % DEFAULT_NGO_ADMIN_EMAIL))

                admin_group_name = utils.get_ngo_group_name(bos_ngo, GroupType.ADMIN.value)
                admin_group, created = Group.objects.get_or_create(name=admin_group_name)
                bos_admin.groups.add(admin_group)
                try:
                    code_name = 'bos_admin'
                    name = 'bos admin'
                    permission = Permission.objects.get(codename=code_name, name=name)
                    bos_admin.user_permissions.add(permission)
                    self.stdout.write(self.style.SUCCESS('Added "%s" permission to admin_group' % name))
                except Permission.DoesNotExist:
                    logging.warning("Permission not found with codename '{}' name '{}'.".format(code_name, name))

                for code_name, name, _ in DEFAULT_PERMISSIONS_ADMIN:
                    try:
                        permission = Permission.objects.get(codename=code_name, name=name)
                        # TODO
                        # ct = ContentType.objects.get_for_model(Project)
                        admin_group.permissions.add(permission)
                        self.stdout.write(self.style.SUCCESS('Added "%s" permission to admin_group' % name))
                    except Permission.DoesNotExist:
                        logging.warning("Permission not found with codename '{}' name '{}'.".format(code_name, name))
                        continue

                # Add bos admin permissions to bos admin


                # Create default Student baselines

                student_baseline_measurement_type = MeasurementType.objects.get(
                    label=DefaultMeasurementType.STUDENT_BASELINE.value)
                for student_baseline,input_type,uom in DEFAULT_STUDENT_BASELINES:
                    try:
                        _ = Measurement.objects.get(label=student_baseline,
                                                    types=student_baseline_measurement_type)
                    except Measurement.DoesNotExist:

                        if created:
                            self.stdout.write(
                                self.style.SUCCESS('DefaultMeasurementType "%s" added to database' % student_baseline))
                        else:
                            create_data = {
                                'label': student_baseline,
                                'key': generate_measurement_key(),
                                'uom': "",
                                'types': [student_baseline_measurement_type.key],
                                'input_type': input_type,
                                'ngo': bos_ngo.key,
                                'is_active': True
                            }
                            serializer = MeasurementSerializer(data=create_data)
                            if serializer.is_valid():
                                serializer.save()
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        'DefaultMeasurementType "%s" exists in database' % student_baseline))
                            else:
                                self.stdout.write(
                                    self.style.ERROR(
                                        'DefaultMeasurementType "%s" not added to database' % student_baseline))
                                self.stdout.write(self.style.ERROR('"%s"' % serializer.errors))

                # Create default Student progression

                student_progression_measurement_type = MeasurementType.objects.get(
                    label=DefaultMeasurementType.STUDENT_PROGRESSION.value)
                for student_progression,input_type,uom in DEFAULT_STUDENT_PROGRESSIONS:
                    try:
                        _ = Measurement.objects.get(label=student_progression,
                                                    types=student_progression_measurement_type)
                    except Measurement.DoesNotExist:

                        if created:
                            self.stdout.write(
                                self.style.SUCCESS('DefaultMeasurementType "%s" added to database' % student_progression))
                        else:
                            create_data = {
                                'label': student_progression,
                                'key': generate_measurement_key(),
                                'uom': "",
                                'types': [student_progression_measurement_type.key],
                                'input_type': input_type,
                                'ngo': bos_ngo.key,
                                'is_active': True
                            }
                            serializer = MeasurementSerializer(data=create_data)
                            if serializer.is_valid():
                                serializer.save()
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        'DefaultMeasurementType "%s" exists in database' % student_progression))
                            else:
                                self.stdout.write(
                                    self.style.ERROR(
                                        'DefaultMeasurementType "%s" not added to database' % student_progression))
                                self.stdout.write(self.style.ERROR('"%s"' % serializer.errors))

                # Create default Coach baselines

                coach_baseline_measurement_type = MeasurementType.objects.get(
                    label=DefaultMeasurementType.COACH_BASELINE.value)
                for coach_baseline,input_type,uom in DEFAULT_COACH_BASELINES:
                    try:
                        _ = Measurement.objects.get(label=coach_baseline,
                                                    types=coach_baseline_measurement_type)
                    except Measurement.DoesNotExist:

                        if created:
                            self.stdout.write(
                                self.style.SUCCESS('DefaultMeasurementType "%s" added to database' % coach_baseline))
                        else:
                            create_data = {
                                'label': coach_baseline,
                                'key': generate_measurement_key(),
                                'uom': "",
                                'types': [coach_baseline_measurement_type.key],
                                'input_type': input_type,
                                'ngo': bos_ngo.key,
                                'is_active': True
                            }
                            serializer = MeasurementSerializer(data=create_data)
                            if serializer.is_valid():
                                serializer.save()
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        'DefaultMeasurementType "%s" exists in database' % coach_baseline))
                            else:
                                self.stdout.write(
                                    self.style.ERROR(
                                        'DefaultMeasurementType "%s" not added to database' % coach_baseline))
                                self.stdout.write(self.style.ERROR('"%s"' % serializer.errors))

        except DatabaseError:
            return
