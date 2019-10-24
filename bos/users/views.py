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

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from psycopg2._psycopg import DatabaseError
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bos.defaults import DEFAULT_PERMISSIONS_BLACKLIST, DefaultMeasurementType
from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.utils import user_filters_from_request, get_ngo_group_name, user_group_filters_from_request, \
    convert_validation_error_into_response_error
from measurements.models import Measurement
from users.models import User, UserReading, UserGroup
from users.serializers import UserSerializer, PermissionGroupDetailSerializer, PermissionSerializer, AthleteSerializer, \
    UserReadingSerializer, UserReadingReadOnlySerializer, CoachSerializer, PermissionGroupSerializer, \
    UserGroupReadOnlySerializer, AdminSerializer


class UserViewSet(ViewSet):
    def list(self, request):
        user_filters, search_filters = user_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
            'role': User.ADMIN,
        }
        filters = {**common_filters, **user_filters}

        queryset = User.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = UserSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        serializer = UserSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class AdminViewSet(ViewSet):
    def list(self, request):
        user_filters, search_filters = user_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
            'role': User.ADMIN,
        }
        filters = {**common_filters, **user_filters}

        queryset = User.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = AdminSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        try:
            with transaction.atomic():
                validate_password(password)
                validate_password(confirm_password)
                if confirm_password != password:
                    raise ValidationException({"errors":[{'password':'Passwords do not match'}]})
                serializer = AdminSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                admin = serializer.save()
                admin.set_password(password)
                admin.save()

                return Response(serializer.data, status=201)
        except ValidationException as e:
            return Response(e.errors, status=400)
        except ValidationError as e:
            error = convert_validation_error_into_response_error(e)
            return Response(error, status=400)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = AdminSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        serializer = AdminSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class AthleteViewSet(ViewSet):
    def list(self, request):
        user_filters, search_filters = user_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
            'role': User.ATHLETE,
        }
        filters = {**common_filters, **user_filters}

        queryset = User.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = UserSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        resource = request.data.get('resource', None)
        try:
            with transaction.atomic():
                serializer = AthleteSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                athlete = serializer.save()
                baselines = create_data["baselines"]
                for baseline in baselines:
                    user_reading_data = {}
                    user_reading_data['user'] = athlete.key
                    user_reading_data['ngo'] = request.user.ngo.key
                    user_reading_data['by_user'] = request.user.key
                    user_reading_data['resource'] = resource
                    user_reading_data['entered_by'] = request.user.key
                    user_reading_data['measurement'] = baseline['key']
                    if baseline['input_type'] == Measurement.BOOLEAN:
                        boolean_value = baseline['value']
                        if boolean_value:
                            user_reading_data['value'] = "True"
                        else:
                            user_reading_data['value'] = "False"
                    else:
                        user_reading_data['value'] = baseline['value']
                    user_reading_serializer = UserReadingSerializer(data=user_reading_data)
                    if not user_reading_serializer.is_valid():
                        raise ValidationException(user_reading_serializer.errors)
                    _ = user_reading_serializer.save()

                return Response(serializer.data, status=201)

        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(status=400, data=e.errors)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        serializer = UserSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class CoachViewSet(ViewSet):

    def list(self, request):
        user_filters, search_filters = user_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
            'role': User.COACH,
        }
        filters = {**common_filters, **user_filters}

        queryset = User.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = UserSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        resource = request.data.get('resource',None)
        try:
            with transaction.atomic():
                serializer = CoachSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                # TODO validate measurements belong to the same ngo
                coach = serializer.save()
                baselines = create_data["baselines"]
                for baseline in baselines:
                    user_reading_data = {}
                    user_reading_data['user'] = coach.key
                    user_reading_data['resource'] = resource
                    user_reading_data['ngo'] = request.user.ngo.key
                    user_reading_data['by_user'] = request.user.key
                    user_reading_data['entered_by'] = request.user.key
                    user_reading_data['measurement'] = baseline['key']
                    if baseline['input_type'] == Measurement.BOOLEAN:
                        boolean_value = baseline['value']
                        if boolean_value:
                            user_reading_data['value'] = "True"
                        else:
                            user_reading_data['value'] = "False"
                    else:
                        user_reading_data['value'] = baseline['value']
                    user_reading_serializer = UserReadingSerializer(data=user_reading_data)
                    if not user_reading_serializer.is_valid():
                        raise ValidationException(user_reading_serializer.errors)
                    _ = user_reading_serializer.save()

                return Response(serializer.data, status=201)

        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(status=400, data=e.errors)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        serializer = UserSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class UserGroupViewSet(ViewSet):

    def list(self, request):
        user_group_filters, search_filters = user_group_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
        }
        filters = {**common_filters, **user_group_filters}

        queryset = UserGroup.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = UserGroupReadOnlySerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        #  TODO validation users belong to the same ngo
        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        try:
            with transaction.atomic():
                serializer = UserGroupReadOnlySerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                _ = serializer.save()
                return Response(serializer.data, status=201)

        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(data=e.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = UserGroup.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserGroupReadOnlySerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = UserGroup.objects.get(key=pk)
        except UserGroup.DoesNotExist:
            return Response(status=404)
        serializer = UserGroupReadOnlySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = UserGroup.objects.get(key=pk)
        except UserGroup.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None:
        return Response(status=400)
    if password is None:
        return Response(status=400)
    user = authenticate(username=username, password=password)
    if user is not None:
        # A backend authenticated the credentials
        try:
            login(request._request, user)
        except:
            return Response(status=500)

        data = {'username': user.username,
                'key': user.key,
                'ngo': user.ngo.key if user.ngo else None,
                'ngo_name': user.ngo.name if user.ngo else None,
                'permissions': user.get_all_permissions(),
                'language': user.language,
                'first_name': user.first_name,
                }
        # .update(SUCCESS_LOGIN_1_JSON)
        return Response(data=data, status=200)

    else:
        # No backend authenticated the credentials
        return Response(status=403)


@api_view(['POST'])
def logout_view(request):
    if request.user and request.user.is_authenticated:
        logout(request)
        return Response(status=200)
    else:
        return Response(status=403)


class PermissionGroupViewSet(ViewSet):

    def list(self, request):
        # TODO check if ngo is null
        ngo_key = request.user.ngo.key
        user_filters, search_filters = user_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'name__startswith': ngo_key,
        }
        filters = {**common_filters, **user_filters}

        queryset = Group.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = PermissionGroupDetailSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        # TODO check if ngo is null
        ngo = request.user.ngo
        name = request.data.get('name', None)
        permissions = request.data.get('permissions', None)
        if not name:
            return Response(status=400)
        create_data = request.data.copy()
        create_data['name'] = get_ngo_group_name(ngo, name)

        try:
            with transaction.atomic():
                serializer = PermissionGroupSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)
                group = serializer.save()
                for permission_data in permissions:
                    permission = Permission.objects.get(id=permission_data['id'])
                    group.permissions.add(permission)

                return Response(serializer.data, status=201)

        except Permission.DoesNotExist:
            return Response(status=400)
        except ValidationException as e:
            return Response(e.errors, status=400)

        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        # TODO check if ngo is null

        ngo_key = request.user.ngo.key
        queryset = Group.objects.filter(name__startswith=ngo_key)
        item = get_object_or_404(queryset, pk=pk)
        serializer = PermissionGroupDetailSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # TODO check if ngo is null
        ngo_key = request.user.ngo.key
        try:
            group = Group.objects.get(pk=pk, name__startswith=ngo_key)
        except Group.DoesNotExist:
            return Response(status=404)

        permissions_data = request.data
        for permission_data in permissions_data:
            if permission_data['codename'] in DEFAULT_PERMISSIONS_BLACKLIST:
                return Response(status=400)

        try:
            with transaction.atomic():
                group.permissions.clear()
                for permission_data in permissions_data:
                    permission = Permission.objects.get(id=permission_data['id'],
                                                        name=permission_data['name'],
                                                        codename=permission_data['codename'])
                    group.permissions.add(permission)

        except Permission.DoesNotExist:
            return Response(status=400)

        return Response(status=200)

    def destroy(self, request, pk=None):
        # TODO check if ngo is null
        ngo_key = request.user.ngo.key
        try:
            item = Group.objects.get(name__startswith=ngo_key, pk=pk)
        except Group.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

    @action(methods=['GET'], detail=False)
    def all_permissions(self, request):
        # TODO check if ngo is null

        ngo_key = request.user.ngo.key
        queryset = Permission.objects.all().exclude(codename__in=DEFAULT_PERMISSIONS_BLACKLIST)
        serializer = PermissionSerializer(queryset, many=True, read_only=True)
        return Response(serializer.data)
