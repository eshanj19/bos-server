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
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from psycopg2._psycopg import DatabaseError
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bos import utils
from bos.constants import GroupType, METHOD_POST, METHOD_GET, MESSAGE_KEY
from bos.defaults import DEFAULT_MEASUREMENT_TYPES
from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.permissions import CanChangeCustomUserGroup, DEFAULT_PERMISSIONS_NGO_ADMIN, \
    has_permission, PERMISSION_BOS_ADMIN, BOSAdmin, CanViewPermissionGroup, CanViewFile, CanViewCurriculum, \
    CanViewTrainingSession, CanAddTrainingSession, CanViewUserHierarchy, PERMISSION_CAN_CHANGE_USER, \
    PERMISSION_CAN_CHANGE_ADMIN, PERMISSION_CAN_CHANGE_COACH, CanChangeUserHierarchy, CanViewMeasurement, \
    DEFAULT_PERMISSIONS_COACH, CanViewResource, CanChangeUser, CanChangeCoach, CanChangeAdmin, PERMISSION_CAN_VIEW_NGO, \
    PERMISSION_CAN_ADD_NGO, PERMISSION_CAN_CHANGE_NGO, PERMISSION_CAN_DESTROY_NGO
from bos.utils import ngo_filters_from_request
from measurements.models import generate_measurement_key, Measurement
from measurements.serializers import MeasurementTypeSerializer, MeasurementSerializer, MeasurementDetailSerializer
from ngos.models import NGO, NGORegistrationResource
from ngos.serializers import NGOSerializer, NGORegistrationResourceSerializer, NGORegistrationResourceDetailSerializer
from resources.models import Resource
from resources.serializers import ResourceSerializer, ResourceDetailSerializer
from users.models import User, UserHierarchy
from users.serializers import UserSerializer, PermissionGroupSerializer, UserHierarchyWriteSerializer


class NGOViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_NGO):
            return Response(status=403)

        user_filters, search_filters = ngo_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        filters = {**user_filters}

        queryset = NGO.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = NGOSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_NGO):
            return Response(status=403)

        try:
            with transaction.atomic():
                serializer = NGOSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)
                ngo = serializer.save()
                for measurement_type in DEFAULT_MEASUREMENT_TYPES:
                    measurement_type_data = {"key": generate_measurement_key(), "label": measurement_type,
                                             "ngo": ngo.key, "is_active": True}
                    serializer = MeasurementTypeSerializer(
                        data=measurement_type_data)
                    if not serializer.is_valid():
                        raise ValidationException(serializer.errors)
                    serializer.save()

                first_name = request.data.get('first_name', None)
                last_name = request.data.get('last_name', None)
                password = request.data.get('password', None)
                confirm_password = request.data.get('confirm_password', None)
                email = request.data.get('email', None)
                username = request.data.get('username', None)
                create_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "gender": "male",
                    "username": username,
                    "ngo": ngo.key
                }

                serializer = UserSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                if not password or not confirm_password or (password != confirm_password):
                    raise ValidationException(
                        {"password": "Passwords dont match"})
                validate_password(password=password)

                ngo_admin = serializer.save()
                ngo_admin.set_password(password)
                ngo_admin.save()

                admin_group_name = utils.get_ngo_group_name(
                    ngo, GroupType.ADMIN.value)
                admin_group, created = Group.objects.get_or_create(
                    name=admin_group_name)

                ngo_admin.groups.add(admin_group)
                for code_name, name, _ in DEFAULT_PERMISSIONS_NGO_ADMIN:
                    try:
                        permission = Permission.objects.get(
                            codename=code_name, name=name)
                        admin_group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        continue

                coach_group_name = utils.get_ngo_group_name(
                    ngo, GroupType.COACH.value)
                coach_group, created = Group.objects.get_or_create(
                    name=coach_group_name)

                for code_name, name, _ in DEFAULT_PERMISSIONS_COACH:
                    try:
                        permission = Permission.objects.get(
                            codename=code_name, name=name)
                        coach_group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        continue

                return Response(status=201)
        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(e.errors, status=400)
        except ValidationError as e:
            return Response({"password": e}, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_NGO):
            return Response(status=403)

        queryset = NGO.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = NGOSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_NGO):
            return Response(status=403)

        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        serializer = NGOSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_NGO):
            return Response(status=403)

        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[BOSAdmin])
    def deactivate(self, request, pk=None):
        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.is_active = False
        item.save()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[BOSAdmin])
    def activate(self, request, pk=None):
        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.is_active = True
        item.save()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanViewPermissionGroup])
    def permission_groups(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Group.objects.filter(name__startswith=ngo.key)
        serializer = PermissionGroupSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET])
    def measurements(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Measurement.objects.filter(ngo=ngo, is_active=True)
        serializer = MeasurementSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanViewFile])
    def files(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Resource.objects.filter(
            ngo=ngo, type=Resource.FILE, is_active=True)
        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanViewCurriculum])
    def curricula(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Resource.objects.filter(
            ngo=ngo, type=Resource.CURRICULUM, is_active=True)
        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanViewTrainingSession])
    def training_sessions(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Resource.objects.filter(
            ngo=ngo, type=Resource.TRAINING_SESSION, is_active=True)
        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=[METHOD_GET], permission_classes=[AllowAny])
    def active_ngos(self, request, pk=None):
        ngos = NGO.objects.filter(is_active=True)
        serializer = NGOSerializer(ngos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[AllowAny])
    def coach_registration_form(self, request, pk=None):
        # TODO
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        try:
            ngo_registration_resource = NGORegistrationResource.objects.get(ngo=ngo, type=NGORegistrationResource.COACH)
        except NGORegistrationResource.DoesNotExist:
            return Response(status=404)

        serializer = NGORegistrationResourceDetailSerializer(ngo_registration_resource)
        json = {
            "label": "Coach registration form",
            "type": Resource.TRAINING_SESSION,
            "children": [
                {"label": "Weight", "type": "MEASUREMENT"},
                {"label": "Height", "type": "MEASUREMENT"},
                {"label": "BMI", "type": "MEASUREMENT"},
                {"label": "First Name", "type": "MEASUREMENT"},
                {"label": "Last Name", "type": "MEASUREMENT"},
            ]

        }
        return Response(data=serializer.data.get('resource'))

    @action(detail=True, methods=[METHOD_POST], permission_classes=[CanAddTrainingSession])
    def mark_as_coach_registration_resource(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        if ngo != request.user.ngo:
            return Response(status=400)
        create_data = request.data.copy()
        create_data['type'] = NGORegistrationResource.COACH
        create_data['ngo'] = ngo.key
        # TODO error

        try:
            with transaction.atomic():

                existing_registration_resources = NGORegistrationResource.objects.filter(ngo=ngo,
                                                                                         type=NGORegistrationResource.COACH).all()
                for existing_registration_resource in existing_registration_resources:
                    existing_registration_resource.delete()

                serializer = NGORegistrationResourceSerializer(
                    data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                serializer.save()
        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(e.errors, status=400)

        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[CanAddTrainingSession])
    def mark_as_athlete_registration_resource(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        if ngo != request.user.ngo:
            return Response(status=400)
        create_data = request.data.copy()
        create_data['type'] = NGORegistrationResource.ATHLETE
        create_data['ngo'] = ngo.key

        try:
            _ = Resource.objects.get(key=create_data['resource'], type=Resource.REGISTRATION_FORM)
        except Resource.DoesNotExist:
            return Response(status=404)
        # TODO error

        try:
            with transaction.atomic():

                existing_registration_resources = NGORegistrationResource.objects.filter(ngo=ngo,
                                                                                         type=NGORegistrationResource.ATHLETE).all()
                for existing_registration_resource in existing_registration_resources:
                    existing_registration_resource.delete()

                serializer = NGORegistrationResourceSerializer(
                    data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                serializer.save()
        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(e.errors, status=400)

        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[AllowAny])
    def coach_registration_resource(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        if ngo != request.user.ngo:
            return Response(status=403)
        try:
            resource = NGORegistrationResource.objects.get(
                ngo=ngo, type=NGORegistrationResource.COACH)
        except NGORegistrationResource.DoesNotExist:
            return Response(status=404)

        serializer = NGORegistrationResourceDetailSerializer(resource)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanChangeCustomUserGroup])
    def all_users(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        if ngo != request.user.ngo:
            return Response(status=403)
        try:
            all_users = User.objects.filter(
                ngo=ngo, is_active=True)
        except User.DoesNotExist:
            return Response(status=404)

        serializer = UserSerializer(all_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[AllowAny])
    def athlete_registration_resource(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        try:
            resource = NGORegistrationResource.objects.get(
                ngo=ngo, type=NGORegistrationResource.ATHLETE, resource__is_active=True)
        except NGORegistrationResource.DoesNotExist:
            return Response(status=404)

        serializer = NGORegistrationResourceDetailSerializer(resource)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanViewUserHierarchy])
    def user_hierarchy(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        response_data = []
        active_users = User.objects.filter(ngo=ngo, is_active=True)
        ghost_node = {}
        ghost_node['key'] = "ghost_node"
        ghost_node['parent_node'] = None
        ghost_node['label'] = "Organisation"
        ghost_node_children = []
        for active_user in active_users:
            user = {}
            user['key'] = active_user.key
            user['role'] = active_user.role
            user['label'] = active_user.full_name
            parent_user_user_hierarchy = UserHierarchy.objects.filter(parent_user__is_active=True,
                                                                      child_user=active_user).first()
            if parent_user_user_hierarchy:
                user['parent_node'] = parent_user_user_hierarchy.parent_user.key
            else:
                user['parent_node'] = None
            child_user_user_hierarchies = UserHierarchy.objects.filter(child_user__is_active=True,
                                                                       parent_user=active_user)
            child_user_keys = []
            for child_user_user_hierarchy in child_user_user_hierarchies:
                child_user_keys.append(child_user_user_hierarchy.child_user.key)
            user['children'] = child_user_keys
            response_data.append(user)

            if user['parent_node'] is None and len(user['children']) != 0:
                ghost_node_children.append(active_user.key)

        ghost_node['children'] = ghost_node_children
        response_data.append(ghost_node)

        return Response(response_data)

    @action(detail=True, methods=[METHOD_POST], permission_classes=[CanChangeUserHierarchy])
    def save_user_hierarchy(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        try:
            with transaction.atomic():
                # clean all UserHierarchy objects for ngo
                ngo_filter = Q(parent_user__ngo=ngo) | Q(child_user__ngo=ngo)
                UserHierarchy.objects.filter(ngo_filter).delete()

                # TODO Check for cycle in binary tree.
                hierarchy_data = request.data.copy()
                for node in hierarchy_data:
                    parent_to_child(node)

        except ValidationException as e:
            return Response(e.errors, status=400)
        return Response(status=201, data={MESSAGE_KEY: 'Organization updated'})

    @action(detail=True, methods=[METHOD_POST], permission_classes=[AllowAny])
    def measurements_from_keys(self, request, pk=None):
        # TODO
        measurement_keys = request.data.copy()
        if measurement_keys is None or len(measurement_keys) == 0:
            return Response(status=400)

        queryset = Measurement.objects.filter(key__in=measurement_keys, is_active=True)
        serializer = MeasurementDetailSerializer(queryset, read_only=True, many=True)
        return Response(data=serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanViewMeasurement])
    def all_measurements(self, request, pk=None):
        queryset = Measurement.objects.filter(ngo=request.user.ngo)
        serializer = MeasurementDetailSerializer(queryset, read_only=True, many=True)
        return Response(data=serializer.data)

    @action(detail=True, methods=[METHOD_GET], permission_classes=[CanChangeUser,
                                                                   CanChangeAdmin,
                                                                   CanChangeCoach])
    def all_resources(self, request, pk=None):
        queryset = Resource.objects.filter(ngo=request.user.ngo)
        serializer = ResourceDetailSerializer(queryset, read_only=True, many=True)
        return Response(data=serializer.data)


def parent_to_child(hierarchy_data):
    parent_key = hierarchy_data.get('key', None)
    children = hierarchy_data.get('children', [])
    children_keys = []
    for child in children:
        child_key = child.get('key', None)
        if not child_key:
            # print("Child key is None")
            raise ValidationException()

        children_keys.append(child_key)

    if parent_key == 'ghost_node':
        parent_key = None

        # Write to user hierarchy
    for child_key in children_keys:
        create_data = {'parent_user': parent_key, 'child_user': child_key}
        serializer = UserHierarchyWriteSerializer(data=create_data)
        if not serializer.is_valid():
            raise ValidationException(serializer.errors)
        serializer.save()

    for child in children:
        parent_to_child(child)


class PingViewSet(ViewSet):

    def list(self, request):
        return Response(status=200)

    def create(self, request):
        return Response(status=201)

    def retrieve(self, request, pk=None):
        return Response(status=200)

    def update(self, request, pk=None):
        return Response(status=200)

    def destroy(self, request, pk=None):
        return Response(status=204)
