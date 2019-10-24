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

from django.contrib.auth.models import Group, Permission
from rest_framework.fields import CharField, BooleanField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from measurements.models import Measurement
from measurements.serializers import MeasurementSerializer
from ngos.models import NGO
from resources.models import Resource
from users.models import User, UserHierarchy, generate_username, UserReading, UserResource, UserGroup


class UserSerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    role = CharField(default=User.ADMIN)
    is_active = BooleanField(default=True)

    class Meta:
        model = User
        exclude = ('id',)


class AdminSerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    role = CharField(default=User.ADMIN)
    is_active = BooleanField(default=True)

    class Meta:
        model = User
        exclude = ('id',)


class AthleteSerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    username = CharField(default=generate_username)
    role = CharField(default=User.ATHLETE)
    is_active = BooleanField(default=True)

    class Meta:
        model = User
        exclude = ('id',)


class CoachSerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    username = CharField(default=generate_username)
    role = CharField(default=User.COACH)
    is_active = BooleanField(default=True)

    class Meta:
        model = User
        exclude = ('id',)


class UserReadingSerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    user = SlugRelatedField(slug_field='key', queryset=User.objects.all())
    by_user = SlugRelatedField(slug_field='key', queryset=User.objects.all())
    entered_by = SlugRelatedField(slug_field='key', queryset=User.objects.all())
    measurement = SlugRelatedField(slug_field='key', queryset=Measurement.objects.all())
    measurement_object = MeasurementSerializer(read_only=True)
    # resource = SlugRelatedField(slug_field='key', queryset=Resource.objects.all(),default=None)
    is_active = BooleanField(default=True)

    class Meta:
        model = UserReading
        exclude = ('id',)


class UserReadingReadOnlySerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    user = SlugRelatedField(slug_field='key', queryset=User.objects.all())
    by_user = SlugRelatedField(slug_field='key', queryset=User.objects.all())
    entered_by = SlugRelatedField(slug_field='key', queryset=User.objects.all())
    measurement = MeasurementSerializer(read_only=True)
    is_active = BooleanField(default=True)

    class Meta:
        model = UserReading
        exclude = ('id',)


class UserGroupReadOnlySerializer(ModelSerializer):
    lookup_field = 'key'
    pk_field = 'key'
    ngo = SlugRelatedField(slug_field='key', queryset=NGO.objects.all())
    users = SlugRelatedField(slug_field='key', queryset=User.objects.all(), many=True)
    resources = SlugRelatedField(slug_field='key', queryset=Resource.objects.all(), many=True)
    is_active = BooleanField(default=True)

    class Meta:
        model = UserGroup
        exclude = ('id',)


class UserHierarchySerializer(ModelSerializer):
    class Meta:
        model = UserHierarchy
        exclude = ('id',)


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        # exclude = ('id',)
        fields = ('id', 'name', 'codename')


class PermissionGroupDetailSerializer(ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        # exclude = ('id',)
        fields = ('id', 'name', 'permissions')
        depth = 2


class PermissionGroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        # exclude = ('id',)
        fields = ('id', 'name',)


class UserResourceSerializer(ModelSerializer):
    class Meta:
        model = UserResource
        exclude = ('id',)


class UserGroupSerializer(ModelSerializer):
    class Meta:
        model = UserGroup
        exclude = ('id',)
