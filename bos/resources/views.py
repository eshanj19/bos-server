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
import json

from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404
# Create your views here.
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bos.constants import METHOD_POST
from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.permissions import has_permission, PERMISSION_CAN_VIEW_RESOURCE, PERMISSION_CAN_ADD_FILE, \
    PERMISSION_CAN_ADD_CURRICULUM, PERMISSION_CAN_ADD_TRAINING_SESSION, PERMISSION_CAN_CHANGE_FILE, \
    PERMISSION_CAN_CHANGE_CURRICULUM, PERMISSION_CAN_CHANGE_TRAINING_SESSION, PERMISSION_CAN_DESTROY_RESOURCE, \
    PERMISSION_CAN_ADD_REGISTRATION_FORM, PERMISSION_CAN_CHANGE_REGISTRATION_FORM
from bos.utils import resource_filters_from_request, error_403_json, error_400_json, request_user_belongs_to_resource
from resources.models import Resource
from resources.serializers import ResourceSerializer


class ResourceViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_RESOURCE):
            return Response(status=403, data=error_403_json())

        resource_filters, search_filters = resource_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
        }
        filters = {**common_filters, **resource_filters}

        queryset = Resource.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = ResourceSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):

        create_data = request.data.copy()
        create_data['ngo'] = request.user.ngo.key

        resource_type = request.data.get('type', None)
        resource_data = request.data.get('data', None)
        if type(resource_data) == list:
            return Response(status=400, data=error_400_json())
        if not resource_type:
            return Response(status=400, data=error_400_json())
        if resource_type == Resource.FILE and not has_permission(request, PERMISSION_CAN_ADD_FILE):
            print("No permission")
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.CURRICULUM and not has_permission(request, PERMISSION_CAN_ADD_CURRICULUM):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.TRAINING_SESSION and not has_permission(request,
                                                                             PERMISSION_CAN_ADD_TRAINING_SESSION):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.REGISTRATION_FORM and not has_permission(request,
                                                                              PERMISSION_CAN_ADD_REGISTRATION_FORM):
            return Response(status=403, data=error_403_json())

        if resource_type == Resource.FILE:
            #  TODO Saving POST'ed file to storage
            file = request.FILES['file']
            file_name = default_storage.save(file.name, file)

            #  Reading file from storage
            file = default_storage.open(file_name)
            file_url = default_storage.url(file_name)
            create_data['data'] = json.dumps({'url': file_url})
        try:
            with transaction.atomic():
                serializer = ResourceSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                serializer.save()
                return Response(serializer.data, status=201)

        except ValidationException as e:
            return Response(status=400, data=e.errors)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_RESOURCE):
            return Response(status=403, data=error_403_json())

        queryset = Resource.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = ResourceSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        resource_type = request.data.get('type', None)
        if not resource_type:
            return Response(status=400, data=error_400_json())
        if resource_type == Resource.FILE and not has_permission(request, PERMISSION_CAN_CHANGE_FILE):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.CURRICULUM and not has_permission(request, PERMISSION_CAN_CHANGE_CURRICULUM):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.TRAINING_SESSION and not has_permission(request,
                                                                             PERMISSION_CAN_CHANGE_TRAINING_SESSION):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.REGISTRATION_FORM and not has_permission(request,
                                                                              PERMISSION_CAN_CHANGE_REGISTRATION_FORM):
            return Response(status=403, data=error_403_json())

        try:
            resource = Resource.objects.get(key=pk)
        except Resource.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_resource(request, resource):
            return Response(status=403, data=error_403_json())

        update_data = request.data.copy()
        update_data['ngo'] = request.user.ngo.key
        resource_data = request.data.get('data', None)
        if type(resource_data) == list:
            return Response(status=400, data=error_400_json())

        if resource.type == Resource.FILE:
            update_data['data'] = json.dumps(resource.data)
        serializer = ResourceSerializer(resource, data=update_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_RESOURCE):
            return Response(status=403, data=error_403_json())

        try:
            resource = Resource.objects.get(key=pk)
        except Resource.DoesNotExist:
            return Response(status=404)

        if not request_user_belongs_to_resource(request, resource):
            return Response(status=403, data=error_403_json())

        resource.delete()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_POST])
    def deactivate(self, request, pk=None):
        ngo = request.user.ngo
        try:
            resource = Resource.objects.get(key=pk, ngo=ngo)
        except Resource.DoesNotExist:
            return Response(status=404)

        resource_type = resource.type
        if not resource_type:
            return Response(status=400, data=error_400_json())
        if resource_type == Resource.FILE and not has_permission(request, PERMISSION_CAN_CHANGE_FILE):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.CURRICULUM and not has_permission(request, PERMISSION_CAN_CHANGE_CURRICULUM):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.TRAINING_SESSION and not has_permission(request,
                                                                             PERMISSION_CAN_CHANGE_TRAINING_SESSION):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.REGISTRATION_FORM and not has_permission(request,
                                                                              PERMISSION_CAN_CHANGE_REGISTRATION_FORM):
            return Response(status=403, data=error_403_json())

        resource.is_active = False
        resource.save()
        return Response(status=204)

    @action(detail=True, methods=[METHOD_POST])
    def activate(self, request, pk=None):
        ngo = request.user.ngo
        try:
            resource = Resource.objects.get(key=pk, ngo=ngo)
        except Resource.DoesNotExist:
            return Response(status=404)

        resource_type = resource.type
        if not resource_type:
            return Response(status=400, data=error_400_json())
        if resource_type == Resource.FILE and not has_permission(request, PERMISSION_CAN_CHANGE_FILE):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.CURRICULUM and not has_permission(request, PERMISSION_CAN_CHANGE_CURRICULUM):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.TRAINING_SESSION and not has_permission(request,
                                                                             PERMISSION_CAN_CHANGE_TRAINING_SESSION):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.REGISTRATION_FORM and not has_permission(request,
                                                                              PERMISSION_CAN_CHANGE_REGISTRATION_FORM):
            return Response(status=403, data=error_403_json())

        resource.is_active = True
        resource.save()
        return Response(status=204)
