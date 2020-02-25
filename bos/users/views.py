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
from datetime import timedelta, timezone, datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bos.constants import METHOD_GET
from bos.constants import METHOD_POST
from bos.defaults import DEFAULT_PERMISSIONS_BLACKLIST
from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.permissions import has_permission, PERMISSION_CAN_ADD_USER, PERMISSION_CAN_VIEW_USER, \
    PERMISSION_CAN_CHANGE_USER, PERMISSION_CAN_DESTROY_USER, PERMISSION_CAN_VIEW_ADMIN, PERMISSION_CAN_ADD_ADMIN, \
    PERMISSION_CAN_DESTROY_ADMIN, PERMISSION_CAN_CHANGE_ADMIN, PERMISSION_CAN_VIEW_ATHLETE, PERMISSION_CAN_ADD_ATHLETE, \
    PERMISSION_CAN_CHANGE_ATHLETE, PERMISSION_CAN_DESTROY_ATHLETE, PERMISSION_CAN_VIEW_COACH, \
    PERMISSION_CAN_DESTROY_COACH, PERMISSION_CAN_CHANGE_COACH, PERMISSION_CAN_ADD_COACH, \
    PERMISSION_CAN_VIEW_CUSTOM_USER_GROUP, PERMISSION_CAN_ADD_CUSTOM_USER_GROUP, \
    PERMISSION_CAN_CHANGE_CUSTOM_USER_GROUP, PERMISSION_CAN_DESTROY_CUSTOM_USER_GROUP, \
    PERMISSION_CAN_VIEW_PERMISSION_GROUP, PERMISSION_CAN_DESTROY_PERMISSION_GROUP, \
    PERMISSION_CAN_CHANGE_PERMISSION_GROUP, PERMISSION_CAN_ADD_PERMISSION_GROUP, PERMISSION_CAN_VIEW_READING, \
    PERMISSION_CAN_DESTROY_READING, PERMISSION_CAN_ADD_READING, CanViewPermissionGroup, CanChangeCoach
from bos.utils import user_filters_from_request, get_ngo_group_name, user_group_filters_from_request, \
    convert_validation_error_into_response_error, error_400_json, request_user_belongs_to_user_ngo, error_403_json, \
    request_user_belongs_to_user_group_ngo, find_athletes_under_user, \
    user_reading_filters_from_request, request_status, request_user_belongs_to_reading, error_checkone, \
    user_request_filters_from_request, request_user_belongs_to_user_request_ngo
from measurements.models import Measurement
from resources.models import Resource, EvaluationResource
from resources.serializers import ResourceDetailSerializer, EvaluationResourceDetailSerializer
from users.models import User, UserGroup, UserResource, MobileAuthToken, UserReading, UserRequest
from users.serializers import UserSerializer, PermissionGroupDetailSerializer, PermissionSerializer, AthleteSerializer, \
    UserReadingSerializer, CoachSerializer, PermissionGroupSerializer, \
    UserGroupReadOnlySerializer, AdminSerializer, UserResourceSerializer, UserResourceDetailSerializer, \
    UserGroupDetailSerializer, UserReadingWriteOnlySerializer, UserReadingReadOnlySerializer, \
    UserHierarchyWriteSerializer, \
    UserEditRestrictedDetailSerializer, UserRequestReadOnlySerializer, UserRequestWriteOnlySerializer


class UserViewSet(ViewSet):
    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_USER):
            return Response(status=403, data=error_403_json())

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
        if not has_permission(request, PERMISSION_CAN_ADD_USER):
            return Response(status=403, data=error_403_json())

        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_USER):
            return Response(status=403, data=error_403_json())

        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_USER):
            return Response(status=403, data=error_403_json())

        try:
            user = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, user):
            return Response(status=403, data=error_403_json())

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_USER):
            return Response(status=403, data=error_403_json())

        try:
            user = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, user):
            return Response(status=403, data=error_403_json())
        user.delete()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[IsAuthenticated])
    def resources(self, request, pk=None):
        try:
            user = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        queryset = Resource.objects.filter(Q(is_active=True) & (
                Q(userresource__user=user) | Q(ngoregistrationresource__ngo=request.user.ngo) |
                Q(usergroup__users__in=[user]))).distinct()
        serializer = ResourceDetailSerializer(queryset, many=True)
        return Response(data=serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[IsAuthenticated])
    def groups(self, request, pk=None):
        queryset = UserGroup.objects.filter(users__in=[request.user], ngo=request.user.ngo)
        serializer = UserGroupDetailSerializer(queryset, many=True)
        return Response(data=serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[IsAuthenticated])
    def athletes(self, request, pk=None):
        response_data = find_athletes_under_user(request.user)
        return Response(data=response_data)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[IsAuthenticated])
    def reset_password(self, request, pk=None):
        try:
            user = User.objects.get(key=pk)
            if not request_user_belongs_to_user_ngo(request, user):
                return Response(status=403, data=error_403_json())
        except User.DoesNotExist:
            return Response(status=404)
        try:
            password = request.data.get('password')
            confirm_password = request.data.get('confirmPassword')
            current_password = request.data.get('currentpassword')
            if not check_password(current_password, user.password):
                message = "current password is wrong"
                return Response(status=400, data=error_checkone(message))
            if confirm_password != password:
                message = "Confirm password do not match"
                return Response(status=400, data=error_checkone(message))
            if current_password == password:
                message = "old and new passwords should not be same"
                return Response(status=400, data=error_checkone(message))
            validate_password(password)
            user.set_password(password)
            user.save()
            return Response(status=201)
        except ValidationError as e:
            error = convert_validation_error_into_response_error(e)
            return Response(error, status=400)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[IsAuthenticated])
    def change_language(self, request, pk=None):
        try:
            user = User.objects.get(key=pk)
            if not request_user_belongs_to_user_ngo(request, user):
                return Response(status=403, data=error_403_json())
        except User.DoesNotExist:
            return Response(status=404)

        language = request.data.get('language', None)
        if not language or language not in User.SUPPORTED_LANGUAGES:
            return Response(status=400)

        user.language = language
        user.save()
        return Response(status=200)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[IsAuthenticated])
    def readings(self, request, pk=None):
        try:
            user = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, user):
            return Response(status=403, data=error_403_json())

        queryset = UserReading.objects.filter(user=user)
        serializer = UserReadingReadOnlySerializer(queryset, many=True)
        return Response(data=serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[IsAuthenticated])
    def evaluation_resources(self, request, pk=None):
        try:
            user = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, user):
            return Response(status=403, data=error_403_json())

        queryset = EvaluationResource.objects.filter(user=user, ngo=request.user.ngo, is_evaluated=False)
        serializer = EvaluationResourceDetailSerializer(queryset, many=True)
        return Response(data=serializer.data)


class AdminViewSet(ViewSet):
    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_ADMIN):
            return Response(status=403, data=error_403_json())

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
        if not has_permission(request, PERMISSION_CAN_ADD_ADMIN):
            return Response(status=403, data=error_403_json())

        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        try:
            with transaction.atomic():
                validate_password(password)
                validate_password(confirm_password)
                if confirm_password != password:
                    raise ValidationException([{'password': 'Passwords do not match'}])
                serializer = AdminSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                admin = serializer.save()
                admin.set_password(password)
                admin.save()

                for group_id in request.data.get('permission_groups', []):
                    group = Group.objects.get(id=group_id, name__startswith=request.user.ngo.key)
                    admin.groups.add(group)

                return Response(serializer.data, status=201)
        except ValidationException as e:
            return Response(e.errors, status=400)
        except ValidationError as e:
            error = convert_validation_error_into_response_error(e)
            return Response(error, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_ADMIN):
            return Response(status=403, data=error_403_json())

        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserEditRestrictedDetailSerializer(item)
        admin_data = serializer.data
        admin_data['permission_groups'] = admin_data['groups']
        return Response(admin_data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_ADMIN):
            return Response(status=403, data=error_403_json())

        try:
            admin = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, admin):
            return Response(status=403, data=error_403_json())

        try:
            with transaction.atomic():
                serializer = AdminSerializer(admin, data=request.data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                admin = serializer.save()
                admin.groups.clear()
                for group_id in request.data.get('permission_groups', []):
                    group = Group.objects.get(id=group_id, name__startswith=request.user.ngo.key)
                    admin.groups.add(group)
                return Response(serializer.data)

        except ValidationException as e:
            return Response(status=400, data=e.errors)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_ADMIN):
            return Response(status=403, data=error_403_json())

        try:
            admin = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, admin):
            return Response(status=403, data=error_403_json())

        admin.delete()
        return Response(status=204)


class AthleteViewSet(ViewSet):
    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_ATHLETE):
            return Response(status=403, data=error_403_json())
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
        if not has_permission(request, PERMISSION_CAN_ADD_ATHLETE):
            return Response(status=403, data=error_403_json())

        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        resource = request.data.get('resource', None)
        try:
            with transaction.atomic():
                serializer = AthleteSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                athlete = serializer.save()

                # Create entry in user hierarchy if user is a coach

                if request.user.role == User.COACH:
                    create_data = {'parent_user': request.user.key, 'child_user': athlete.key}
                    user_hierarchy_serializer = UserHierarchyWriteSerializer(data=create_data)
                    if not user_hierarchy_serializer.is_valid():
                        raise ValidationException(user_hierarchy_serializer.errors)
                    user_hierarchy_serializer.save()

                baselines = create_data.get("baselines", [])
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
        if not has_permission(request, PERMISSION_CAN_VIEW_ATHLETE):
            return Response(status=403, data=error_403_json())

        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserEditRestrictedDetailSerializer(item)
        athlete_data = serializer.data
        athlete_resources = UserResource.objects.filter(user=item)
        athlete_resources_serializer = UserResourceDetailSerializer(athlete_resources, many=True)
        resource_keys = []
        for resource_data in athlete_resources_serializer.data:
            resource_keys.append(resource_data.get('resource').get('key'))
        athlete_data['resources'] = resource_keys
        return Response(athlete_data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_ATHLETE):
            return Response(status=403, data=error_403_json())

        try:
            athlete = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, athlete):
            return Response(status=403, data=error_403_json())

        try:
            with transaction.atomic():
                serializer = UserSerializer(athlete, data=request.data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)
                athlete = serializer.save()

                #  Delete all resources attached to user
                UserResource.objects.filter(user=athlete).delete()
                for resource_key in request.data.get('resources', []):
                    resource = Resource.objects.get(key=resource_key, ngo=request.user.ngo)
                    create_data = {'user': athlete.key, 'resource': resource.key}
                    user_resource_serializer = UserResourceSerializer(data=create_data)
                    if not user_resource_serializer.is_valid():
                        raise ValidationException(user_resource_serializer.errors)
                    user_resource_serializer.save()

                return Response(serializer.data, status=201)
        except ValidationException as e:
            return Response(e.errors, status=400)
        except ValidationError as e:
            error = convert_validation_error_into_response_error(e)
            return Response(error, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_ATHLETE):
            return Response(status=403, data=error_403_json())

        try:
            athlete = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)
        if not request_user_belongs_to_user_ngo(request, athlete):
            return Response(status=403, data=error_403_json())

        athlete.delete()
        return Response(status=204)


class CoachViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_COACH):
            return Response(status=403, data=error_403_json())

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
        if not has_permission(request, PERMISSION_CAN_ADD_COACH):
            return Response(status=403, data=error_403_json())

        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        try:
            with transaction.atomic():
                if confirm_password != password:
                    raise ValidationException([{'password': 'Passwords do not match'}])
                validate_password(password)
                validate_password(confirm_password)

                serializer = CoachSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                # TODO validate measurements belong to the same ngo

                coach = serializer.save()
                coach.set_password(password)
                coach.save()

                # baselines = create_data.get("baselines", [])
                # for baseline in baselines:
                #     user_reading_data = {}
                #     user_reading_data['user'] = coach.key
                #     user_reading_data['resource'] = resource
                #     user_reading_data['ngo'] = request.user.ngo.key
                #     user_reading_data['by_user'] = request.user.key
                #     user_reading_data['entered_by'] = request.user.key
                #     user_reading_data['measurement'] = baseline['key']
                #     if baseline['input_type'] == Measurement.BOOLEAN:
                #         boolean_value = baseline['value']
                #         if boolean_value:
                #             user_reading_data['value'] = "True"
                #         else:
                #             user_reading_data['value'] = "False"
                #     else:
                #         user_reading_data['value'] = baseline['value']
                #     user_reading_serializer = UserReadingSerializer(data=user_reading_data)
                #     if not user_reading_serializer.is_valid():
                #         raise ValidationException(user_reading_serializer.errors)
                #     _ = user_reading_serializer.save()

                return Response(serializer.data, status=201)

        except IntegrityError as e:
            return Response(status=400, data=[{'username': 'This username is taken'}])
        except ValidationException as e:
            return Response(status=400, data=e.errors)
        except ValidationError as e:
            return Response(status=400, data=e.errors)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_COACH):
            return Response(status=403, data=error_403_json())

        queryset = User.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserEditRestrictedDetailSerializer(item)
        coach_data = serializer.data
        coach_resources = UserResource.objects.filter(user=item)
        coach_resources_serializer = UserResourceDetailSerializer(coach_resources, many=True)
        resource_keys = []
        for resource_data in coach_resources_serializer.data:
            resource_keys.append(resource_data.get('resource').get('key'))
        coach_data['resources'] = resource_keys
        coach_data['permission_groups'] = coach_data['groups']
        return Response(coach_data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_COACH):
            return Response(status=403, data=error_403_json())

        try:
            coach = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, coach):
            return Response(status=403, data=error_403_json())

        try:
            with transaction.atomic():
                serializer = CoachSerializer(coach, data=request.data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)
                coach = serializer.save()
                coach.groups.clear()
                for group_id in request.data.get('permission_groups', []):
                    group = Group.objects.get(id=group_id, name__startswith=request.user.ngo.key)
                    coach.groups.add(group)

                #  Delete all resources attached to user
                UserResource.objects.filter(user=coach).delete()
                for resource_key in request.data.get('resources', []):
                    resource = Resource.objects.get(key=resource_key, ngo=request.user.ngo)
                    create_data = {'user': coach.key, 'resource': resource.key}
                    user_resource_serializer = UserResourceSerializer(data=create_data)
                    if not user_resource_serializer.is_valid():
                        raise ValidationException(user_resource_serializer.errors)
                    user_resource_serializer.save()

                return Response(serializer.data, status=201)
        except ValidationException as e:
            return Response(e.errors, status=400)
        except ValidationError as e:
            error = convert_validation_error_into_response_error(e)
            return Response(error, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_COACH):
            return Response(status=403, data=error_403_json())

        try:
            coach = User.objects.get(key=pk)
        except User.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_ngo(request, coach):
            return Response(status=403, data=error_403_json())
        coach.delete()
        return Response(status=204)


class UserGroupViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_CUSTOM_USER_GROUP):
            return Response(status=403, data=error_403_json())

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
        if not has_permission(request, PERMISSION_CAN_ADD_CUSTOM_USER_GROUP):
            return Response(status=403, data=error_403_json())

        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key
        for user_key in request.data.get('users', []):
            try:
                _ = User.objects.get(key=user_key, ngo=request.user.ngo)
            except User.DoesNotExist:
                return Response(status=400)
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
        if not has_permission(request, PERMISSION_CAN_VIEW_CUSTOM_USER_GROUP):
            return Response(status=403, data=error_403_json())

        queryset = UserGroup.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserGroupReadOnlySerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_CUSTOM_USER_GROUP):
            return Response(status=403, data=error_403_json())

        try:
            user_group = UserGroup.objects.get(key=pk)
        except UserGroup.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_group_ngo(request, user_group):
            return Response(status=403, data=error_403_json())

        serializer = UserGroupReadOnlySerializer(user_group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_CUSTOM_USER_GROUP):
            return Response(status=403, data=error_403_json())

        try:
            user_group = UserGroup.objects.get(key=pk)
        except UserGroup.DoesNotExist:
            return Response(status=404)
        if not request_user_belongs_to_user_group_ngo(request, user_group):
            return Response(status=403, data=error_403_json())
        user_group.delete()
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
        if not has_permission(request, PERMISSION_CAN_VIEW_PERMISSION_GROUP):
            return Response(status=403, data=error_403_json())

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
        serializer = PermissionGroupSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_PERMISSION_GROUP):
            return Response(status=403, data=error_403_json())

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
        if not has_permission(request, PERMISSION_CAN_VIEW_PERMISSION_GROUP):
            return Response(status=403, data=error_403_json())

        ngo_key = request.user.ngo.key
        queryset = Group.objects.filter(name__startswith=ngo_key)
        item = get_object_or_404(queryset, pk=pk)
        serializer = PermissionGroupDetailSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_PERMISSION_GROUP):
            return Response(status=403, data=error_403_json())

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
        if not has_permission(request, PERMISSION_CAN_DESTROY_PERMISSION_GROUP):
            return Response(status=403, data=error_403_json())

        ngo_key = request.user.ngo.key
        try:
            item = Group.objects.get(name__startswith=ngo_key, pk=pk)
        except Group.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

    @action(methods=['GET'], detail=False, permission_classes=[CanViewPermissionGroup])
    def all_permissions(self, request):
        queryset = Permission.objects.all().exclude(codename__in=DEFAULT_PERMISSIONS_BLACKLIST)
        serializer = PermissionSerializer(queryset, many=True, read_only=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[CanViewPermissionGroup])
    def show(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_PERMISSION_GROUP):
            return Response(status=403, data=error_403_json())

        ngo_key = request.user.ngo.key
        queryset = Group.objects.filter(name__startswith=ngo_key)
        item = get_object_or_404(queryset, pk=pk)
        serializer = PermissionGroupDetailSerializer(item)
        return Response(serializer.data)


class UserReadingViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_READING):
            return Response(status=403, data=error_403_json())

        user_reading_filters, search_filters = user_reading_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
        }
        filters = {**common_filters, **user_reading_filters}

        queryset = UserReading.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = UserReadingReadOnlySerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_READING):
            return Response(status=403, data=error_403_json())

        create_data = request.data.copy()

        try:
            user_reading_data = {}
            user_reading_data['user'] = create_data.get('user', None)
            user_reading_data['ngo'] = create_data.get('ngo', None)
            user_reading_data['training_session_uuid'] = create_data.get('training_session_uuid', None)
            user_reading_data['evaluation_resource_uuid'] = create_data.get('evaluation_resource_uuid', None)
            user_reading_data['measurement'] = create_data.get('measurement', None)
            user_reading_data['recorded_at'] = create_data.get('recorded_at', None)
            user_reading_data['value'] = create_data.get('value', None)
            user_reading_data['by_user'] = request.user.key
            user_reading_data['entered_by'] = request.user.key

            # TODO Check user measurement belong to the same ngo

            user_reading_serializer = UserReadingWriteOnlySerializer(data=user_reading_data)
            if not user_reading_serializer.is_valid():
                raise ValidationException(user_reading_serializer.errors)
            user_reading_serializer.save()

            return Response(user_reading_serializer.data, status=201)

        except ValidationException as e:
            return Response(e.errors, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_READING):
            return Response(status=403, data=error_403_json())

        queryset = UserReading.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserReadingSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            user_reading = UserReading.objects.get(key=pk)

        except UserReading.DoesNotExist:
            return Response(status=404)

        user_reading.value = request.data.get('value')
        user_reading.is_active = request.data.get('is_active')
        user_reading.save()
        serializer = UserReadingSerializer(user_reading)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_READING):
            return Response(status=403, data=error_403_json())

        try:
            user_reading = UserReading.objects.get(key=pk)
        except UserReading.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_reading(request, user_reading):
            return Response(status=403, data=error_403_json())

        user_reading.delete()
        return Response(status=204)


class UserRequestViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_COACH):
            return Response(status=403, data=error_403_json())

        user_request_filters, search_filters = user_request_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
        }
        filters = {**common_filters, **user_request_filters}

        queryset = UserRequest.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = UserRequestReadOnlySerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=[METHOD_POST], permission_classes=[AllowAny])
    def create_request(self, request):
        create_data = request.data.copy()

        try:
            user_request_data = {}
            user_request_data['first_name'] = create_data.get('first_name', None)
            user_request_data['middle_name'] = create_data.get('middle_name', None)
            user_request_data['last_name'] = create_data.get('last_name', None)
            user_request_data['gender'] = create_data.get('gender', None)
            user_request_data['ngo'] = create_data.get('ngo', None)
            user_request_data['status'] = UserRequest.PENDING
            user_request_data['role'] = "coach"

            user_request_data['data'] = create_data.get('data', {})
            user_request_serializer = UserRequestWriteOnlySerializer(data=user_request_data)
            if not user_request_serializer.is_valid():
                raise ValidationException(user_request_serializer.errors)
            user_request_serializer.save()

            return Response(user_request_serializer.data, status=201)

        except ValidationException as e:
            return Response(e.errors, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_ADD_COACH):
            return Response(status=403, data=error_403_json())

        queryset = UserRequest.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = UserRequestReadOnlySerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            user_request = UserRequest.objects.get(key=pk)
        except UserReading.DoesNotExist:
            return Response(status=404)

        serializer = UserRequestWriteOnlySerializer(user_request, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_COACH):
            return Response(status=403, data=error_403_json())

        try:
            user_request = UserRequest.objects.get(key=pk)
        except UserReading.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_user_request_ngo(request, user_request):
            return Response(status=403, data=error_403_json())

        user_request.delete()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[IsAuthenticated])
    def check_username(self, request, pk=None):

        try:
            _ = UserRequest.objects.filter(key=pk, status=UserRequest.PENDING).first()

        except UserRequest.DoesNotExist:
            return Response(status=404)
        username = request.data.get("username")
        user = User.objects.filter(username=username).first()
        if not user:
            return Response(data={"username": username})
        else:
            for i in range(1, 100):
                temp_username = username + str(i)
                user = User.objects.filter(username=temp_username).first()
                if user:
                    continue
                break
            return Response(data={"username": temp_username})

    @action(detail=True, methods=[METHOD_POST], permission_classes=[IsAuthenticated])
    def request_accept(self, request, pk=None):

        try:
            user_request = UserRequest.objects.filter(key=pk, status=UserRequest.PENDING).first()
        except UserRequest.DoesNotExist:
            return Response(status=404)

        coach_data = {}
        coach_data['first_name'] = user_request.first_name
        coach_data['middle_name'] = user_request.middle_name
        coach_data['last_name'] = user_request.last_name
        coach_data['status'] = user_request.status
        coach_data['gender'] = user_request.gender
        coach_data['username'] = request.data.get('username')
        coach_data['ngo'] = request.user.ngo.key
        coach_reading_data = user_request.data

        password = request.data.get('password')
        confirm_password = request.data.get('confirmpassword')

        try:
            with transaction.atomic():
                if confirm_password != password:
                    output = _("password do not match")
                    raise ValidationException(output)
                validate_password(password)
                validate_password(confirm_password)

                serializer = CoachSerializer(data=coach_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                coach = serializer.save()
                coach.set_password(password)
                coach.save()

            coach_reading_measurements = coach_reading_data.get('measurements', [])

            for coach_reading_measurement in coach_reading_measurements:
                user_coach_data = {}
                user_coach_data['user'] = coach.key
                user_coach_data['ngo'] = request.user.ngo.key
                user_coach_data['by_user'] = request.user.key
                user_coach_data['entered_by'] = request.user.key
                user_coach_data['measurement'] = coach_reading_measurement['key']
                user_coach_data['value'] = coach_reading_measurement['value']

                user_reading_serializer = UserReadingSerializer(data=user_coach_data)
                if not user_reading_serializer.is_valid():
                    raise ValidationException(user_reading_serializer.errors)
                user_reading_serializer.save()

            user_request.status = UserRequest.APPROVED
            user_request.save()

        except IntegrityError as e:
            message = "username is already taken"
            return Response(status=400, data=error_checkone(message))
        except ValidationException as e:
            return Response(status=400, data=error_checkone(e.errors))
        except ValidationError as e:
            return Response(status=400, data=e.errors)

        message = "Accepted"
        return Response(status=200, data=request_status(message))

    @action(detail=True, methods=[METHOD_POST], permission_classes=[CanChangeCoach])
    def request_reject(self, request, pk=None):
        try:
            user_request = UserRequest.objects.filter(key=pk, status=UserRequest.PENDING).first()

        except UserRequest.DoesNotExist:
            return Response(status=404)

        user_request.status = UserRequest.REJECTED
        user_request.save()

        message = "Rejected"
        return Response(status=200, data=request_status(message))


@api_view(['GET'])
@permission_classes([AllowAny])
def is_authenticated(request):
    if request.user and request.user.is_authenticated:
        return Response(status=200, data={"is_authenticated": True})
    else:
        return Response(status=200, data={"is_authenticated": False})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_mobile_view(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    if username is None:
        return Response(data=error_400_json(), status=400)
    if password is None:
        return Response(data=error_400_json(), status=400)
    user = authenticate(username=username, password=password)
    if user:
        # A backend authenticated the credentials
        expiry_date = datetime.now(tz=timezone.utc) + timedelta(days=30)
        auth_token = MobileAuthToken.objects.create(user=user, expiry_date=expiry_date)
        data = {'username': user.username,
                'key': user.key,
                'ngo': user.ngo.key if user.ngo else None,
                'ngo_name': user.ngo.name if user.ngo else None,
                'permissions': user.get_all_permissions(),
                'role': user.role,
                'gender': user.gender,
                'language': user.language,
                'token': auth_token.token,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'expiry_date': auth_token.expiry_date
                }
        return Response(data=data, status=200)
    else:
        # No backend authenticated the credentials
        return Response(data=error_403_json(), status=403)


@api_view(['POST'])
def logout_mobile_view(request):
    if request.user and request.user.is_authenticated:
        logout(request)
        return Response(status=200)
    else:
        return Response(data=error_403_json(), status=403)


@api_view(['POST'])
def refresh_mobile_token_view(request):
    if request.user and request.user.is_authenticated:
        expiry_date = datetime.now(tz=timezone.utc) + timedelta(days=30)
        auth_token = MobileAuthToken.objects.create(user=request.user, expiry_date=expiry_date)
        return Response(status=200, data={
            'token': auth_token.token,
            'expiry_date': auth_token.expiry_date,
        })
    return Resource
