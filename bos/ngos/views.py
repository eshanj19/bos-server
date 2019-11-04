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
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from psycopg2._psycopg import DatabaseError
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bos import utils
from bos.constants import GroupType, METHOD_POST, METHOD_GET
from bos.defaults import DEFAULT_MEASUREMENT_TYPES
from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.permissions import DEFAULT_PERMISSIONS_ADMIN
from bos.utils import ngo_filters_from_request
from measurements.models import generate_measurement_key, Measurement
from measurements.serializers import MeasurementTypeSerializer, MeasurementSerializer
from ngos.models import NGO, NGORegistrationResource
from ngos.serializers import NGOSerializer, NGORegistrationResourceSerializer, NGORegistrationResourceDetailSerializer
from resources.models import Resource
from resources.serializers import ResourceSerializer
from users.models import User, UserHierarchy
from users.serializers import UserSerializer, PermissionGroupSerializer, UserHierarchySerializer, \
    UserHierarchyWriteSerializer


class NGOViewSet(ViewSet):

    def list(self, request):

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
        # TODO
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
                    "username": username,
                    "ngo": ngo.key
                }

                if not password or not confirm_password or (password != confirm_password):
                    raise ValidationException(
                        {"password": "Passwords dont match"})
                serializer = UserSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                ngo_admin = serializer.save()
                ngo_admin.set_password(password)
                ngo_admin.save()

                admin_group_name = utils.get_ngo_group_name(
                    ngo_admin, GroupType.ADMIN.value)
                admin_group, created = Group.objects.get_or_create(
                    name=admin_group_name)

                ngo_admin.groups.add(admin_group)
                for code_name, name, _ in DEFAULT_PERMISSIONS_ADMIN:
                    try:
                        permission = Permission.objects.get(
                            codename=code_name, name=name)
                        # TODO
                        # ct = ContentType.objects.get_for_model(Project)
                        admin_group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        continue

                return Response(status=201)
        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(e.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = NGO.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = NGOSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
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
        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

    # TODO permissions
    @action(detail=True, methods=[METHOD_POST])
    def deactivate(self, request, pk=None):
        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.is_active = False
        item.save()
        return Response(status=204)

    # TODO permissions
    @action(detail=True, methods=[METHOD_POST])
    def activate(self, request, pk=None):
        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.is_active = True
        item.save()
        return Response(status=204)

        # TODO permissions

    @action(detail=True, methods=[METHOD_GET])
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

    @action(detail=True, methods=[METHOD_GET])
    def files(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Resource.objects.filter(
            ngo=ngo, type=Resource.FILE, is_active=True)
        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET])
    def curricula(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        queryset = Resource.objects.filter(
            ngo=ngo, type=Resource.CURRICULUM, is_active=True)
        serializer = ResourceSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET])
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
        return Resource(status=400)
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

    @action(detail=True, methods=[METHOD_POST])
    def mark_as_coach_registration_resource(self, request, pk=None):
        # TODO
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
                serializer = NGORegistrationResourceSerializer(
                    data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                existing_registration_resources = NGORegistrationResource.objects.filter(ngo=ngo,
                                                                                         type=NGORegistrationResource.COACH).all()
                for existing_registration_resource in existing_registration_resources:
                    print("deleted resource")
                    existing_registration_resource.delete()

                serializer.save()
        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(e.errors, status=400)

        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_POST])
    def mark_as_athlete_registration_resource(self, request, pk=None):
        # TODO
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        if ngo != request.user.ngo:
            return Response(status=400)
        create_data = request.data.copy()
        create_data['type'] = NGORegistrationResource.ATHLETE
        create_data['ngo'] = ngo.key

        # TODO error

        try:
            with transaction.atomic():
                serializer = NGORegistrationResourceSerializer(
                    data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                existing_registration_resources = NGORegistrationResource.objects.filter(ngo=ngo,
                                                                                         type=NGORegistrationResource.ATHLETE).all()
                for existing_registration_resource in existing_registration_resources:
                    existing_registration_resource.delete()

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

    # TODO permissions
    @action(detail=True, methods=[METHOD_GET], permission_classes=[AllowAny])
    def athlete_registration_resource(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)

        try:
            resource = NGORegistrationResource.objects.get(
                ngo=ngo, type=NGORegistrationResource.ATHLETE)
        except NGORegistrationResource.DoesNotExist:
            return Response(status=404)

        serializer = NGORegistrationResourceDetailSerializer(resource)
        return Response(serializer.data)

    @action(detail=True, methods=[METHOD_GET])
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
        ghost_node['label'] = "Ghost node"
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

    @action(detail=True, methods=[METHOD_POST])
    def save_user_hierarchy(self, request, pk=None):
        try:
            ngo = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        
        try:
            with transaction.atomic():
                # TODO clean all UserHierarchy objects for ngo
                ngo_filter = Q(parent_user__ngo=ngo) | Q(child_user__ngo=ngo)
                UserHierarchy.objects.filter(ngo_filter).delete()

                # TODO Check for cycle in binary tree.
                hierarchy_data = request.data.copy()
                for node in hierarchy_data:
                    parent_to_child(node)

        except ValidationException as e:
            return Response(e.errors, status=400)
        return Response(status=201,data={'message':'Org updated'})


def parent_to_child(hierarchy_data):
    parent_key = hierarchy_data.get('key', None)
    children = hierarchy_data.get('children', [])
    children_keys = []
    for child in children:
        child_key = child.get('key', None)
        if not child_key:
            print("Child key is None")
            raise ValidationException()

        children_keys.append(child_key)

    if parent_key == 'ghost_node':
        parent_key = None

        # Write to user hierarchy
    for child_key in children_keys:
        create_data = {'parent_user': parent_key, 'child_user': child_key}
        print(create_data)
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
