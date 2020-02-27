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
from django.db.models import Q
from psycopg2._psycopg import DatabaseError

from bos import utils
from bos.constants import GroupType
from bos.defaults import DEFAULT_NGO, DEFAULT_NGO_ADMIN_EMAIL, DEFAULT_NGO_ADMIN_FIRST_NAME, \
    DEFAULT_NGO_ADMIN_LAST_NAME, DEFAULT_NGO_ADMIN_USERNAME, DefaultMeasurementType, DEFAULT_STUDENT_PROGRESSIONS
from bos.exceptions import ValidationException
from bos.permissions import DEFAULT_PERMISSIONS_BOS_NGO_ADMIN
from measurements.models import MeasurementType, Measurement, generate_measurement_key
from measurements.serializers import MeasurementSerializer
from ngos.models import NGO
from users.models import User, generate_user_key, UserHierarchy
from users.serializers import UserSerializer, CoachSerializer, AthleteSerializer, UserHierarchyWriteSerializer


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
                    return
                try:
                    bos_admin = User.objects.get(email=DEFAULT_NGO_ADMIN_EMAIL)
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

                # Create default Coach baselines

                student_progression_measurement_type = MeasurementType.objects.get(
                    label=DefaultMeasurementType.STUDENT_PROGRESSION.value)
                for student_progression, input_type, uom in DEFAULT_STUDENT_PROGRESSIONS:
                    try:
                        _ = Measurement.objects.get(label=student_progression,
                                                    types=student_progression_measurement_type)
                    except Measurement.DoesNotExist:

                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    'DefaultMeasurementType "%s" added to database' % student_progression))
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
                # for code_name, name, _ in DEFAULT_PERMISSIONS_BOS_NGO_ADMIN:
                #     try:
                #         permission = Permission.objects.get(codename=code_name, name=name)
                #         # TODO
                #         # ct = ContentType.objects.get_for_model(Project)
                #         admin_group.permissions.add(permission)
                #         self.stdout.write(self.style.SUCCESS('Added "%s" permission to admin_group' % name))
                #     except Permission.DoesNotExist:
                #         logging.warning("Permission not found with codename '{}' name '{}'.".format(code_name, name))
                #         continue
                #
                # ngo_filter = Q(parent_user__ngo=bos_ngo) | Q(child_user__ngo=bos_ngo)
                # UserHierarchy.objects.filter(ngo_filter).delete()
                #
                # create_data = {'parent_user': None, 'child_user': bos_admin.key}
                # serializer = UserHierarchyWriteSerializer(data=create_data)
                # if not serializer.is_valid():
                #     raise ValidationException(serializer.errors)
                # serializer.save()
                #
                # number_of_coaches = 3
                # athletes_per_coach = 3
                # for i in range(number_of_coaches):
                #     coach_first_name = "Coach"
                #     coach_last_name = i + 1
                #     coach_data = {
                #         'first_name' : coach_first_name,
                #         'last_name' : coach_last_name,
                #         'username': generate_user_key(),
                #         'ngo': bos_ngo.key,
                #         'role': User.COACH
                #     }
                #     serializer = CoachSerializer(data=coach_data)
                #     if not serializer.is_valid():
                #         logging.warning("Unable to create coach")
                #         raise ValidationException(serializer.errors)
                #     coach = serializer.save()
                #
                #
                #     create_data = {'parent_user': bos_admin.key, 'child_user': coach.key}
                #     serializer = UserHierarchyWriteSerializer(data=create_data)
                #     if not serializer.is_valid():
                #         raise ValidationException(serializer.errors)
                #     serializer.save()
                #
                #     for j in range(athletes_per_coach):
                #         athlete_first_name = "Athlete"
                #         athlete_last_name = str(coach_last_name) + " " + str(j+1)
                #         athlete_data = {
                #             'first_name': athlete_first_name,
                #             'last_name': athlete_last_name,
                #             'username': generate_user_key(),
                #             'ngo': bos_ngo.key,
                #             'role': User.ATHLETE
                #         }
                #         serializer = AthleteSerializer(data=athlete_data)
                #         if not serializer.is_valid():
                #             logging.warning("Unable to create athlete")
                #             raise ValidationException(serializer.errors)
                #         athlete = serializer.save()
                #
                #         create_data = {'parent_user': coach.key, 'child_user': athlete.key}
                #         serializer = UserHierarchyWriteSerializer(data=create_data)
                #         if not serializer.is_valid():
                #             raise ValidationException(serializer.errors)
                #         serializer.save()

        except DatabaseError:
            return
        except ValidationException as e:
            print(e.errors)
            return
