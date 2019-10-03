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
from django.db import transaction
from django.shortcuts import get_object_or_404
from psycopg2._psycopg import DatabaseError
from rest_framework.decorators import action
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
from ngos.models import NGO
from ngos.serializers import NGOSerializer
from users.serializers import UserSerializer, PermissionGroupDetailSerializer, PermissionGroupSerializer


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
                    serializer = MeasurementTypeSerializer(data=measurement_type_data)
                    if not serializer.is_valid():
                        raise ValidationException(serializer.errors)
                    serializer.save()

                first_name = request.data.get('first_name',None)
                last_name = request.data.get('last_name',None)
                password = request.data.get('password',None)
                confirm_password = request.data.get('confirm_password',None)
                email = request.data.get('email',None)
                username = request.data.get('username',None)
                create_data= {
                    "first_name" : first_name,
                    "last_name" : last_name,
                    "email" : email,
                    "username" : username,
                    "ngo": ngo.key
                }

                if not password or not confirm_password or (password != confirm_password):
                    raise ValidationException({"password":"Passwords dont match"})
                serializer = UserSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                ngo_admin = serializer.save()
                ngo_admin.set_password(password)
                ngo_admin.save()

                admin_group_name = utils.get_ngo_group_name(ngo_admin, GroupType.ADMIN.value)
                admin_group, created = Group.objects.get_or_create(name=admin_group_name)

                ngo_admin.groups.add(admin_group)
                for code_name, name, _ in DEFAULT_PERMISSIONS_ADMIN:
                    try:
                        permission = Permission.objects.get(codename=code_name, name=name)
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
    @action(detail=True,methods=[METHOD_POST])
    def deactivate(self, request, pk=None):
        try:
            item = NGO.objects.get(key=pk)
        except NGO.DoesNotExist:
            return Response(status=404)
        item.is_active = False
        item.save()
        return Response(status=204)

    # TODO permissions
    @action(detail=True,methods=[METHOD_POST])
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

        queryset = Measurement.objects.filter(ngo=ngo,is_active=True)
        serializer = MeasurementSerializer(queryset, many=True)
        return Response(serializer.data)

