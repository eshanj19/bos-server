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
import os
import pathlib

from django.db import transaction
from django.shortcuts import get_object_or_404
# Create your views here.
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bos.constants import METHOD_POST
from bos.exceptions import ValidationException, SingleMessageValidationException
from bos.pagination import BOSPageNumberPagination
from bos.permissions import has_permission, PERMISSION_CAN_VIEW_RESOURCE, PERMISSION_CAN_ADD_FILE, \
    PERMISSION_CAN_ADD_CURRICULUM, PERMISSION_CAN_ADD_TRAINING_SESSION, PERMISSION_CAN_CHANGE_FILE, \
    PERMISSION_CAN_CHANGE_CURRICULUM, PERMISSION_CAN_CHANGE_TRAINING_SESSION, PERMISSION_CAN_DESTROY_RESOURCE, \
    PERMISSION_CAN_ADD_REGISTRATION_FORM, PERMISSION_CAN_CHANGE_REGISTRATION_FORM, PERMISSION_CAN_ADD_READING
from bos.storage_backends import S3Storage
from bos.utils import resource_filters_from_request, error_403_json, error_400_json, request_user_belongs_to_resource, \
    is_extension_valid, error_file_extension_json, error_500_json
from resources.models import Resource, EvaluationResource
from resources.serializers import ResourceSerializer, EvaluationResourceDetailSerializer, \
    EvaluationResourceUserWriteOnlySerializer, \
    EvaluationResourceGroupWriteOnlySerializer
from users.models import User, UserGroup


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

        resource_type = request.data.get('type', None)
        resource_data = request.data.get('data', None)

        if type(resource_data) == list:
            return Response(status=400, data=error_400_json())
        if not resource_type:
            return Response(status=400, data=error_400_json())
        if resource_type == Resource.FILE and not has_permission(request, PERMISSION_CAN_ADD_FILE):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.CURRICULUM and not has_permission(request, PERMISSION_CAN_ADD_CURRICULUM):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.TRAINING_SESSION and not has_permission(request,
                                                                             PERMISSION_CAN_ADD_TRAINING_SESSION):
            return Response(status=403, data=error_403_json())
        if resource_type == Resource.REGISTRATION_FORM and not has_permission(request,
                                                                              PERMISSION_CAN_ADD_REGISTRATION_FORM):
            return Response(status=403, data=error_403_json())

        create_data = request.data
        create_data['ngo'] = request.user.ngo.key

        try:
            with transaction.atomic():
                if resource_type == Resource.FILE:
                    create_data['data'] = {}
                serializer = ResourceSerializer(data=create_data)

                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)

                resource = serializer.save()

                if resource_type == Resource.FILE:
                    file = request.FILES['file']
                    file_directory_within_bucket = 'ngo_files/{ngo_key}/'.format(ngo_key=request.user.ngo.key)
                    file_extension = pathlib.Path(file.name).suffix
                    if not is_extension_valid(file_extension):
                        raise SingleMessageValidationException(error_file_extension_json())
                    file_label = resource.key
                    file_name = file_label + file_extension
                    # synthesize a full file path; note that we included the filename
                    file_path_within_bucket = os.path.join(
                        file_directory_within_bucket,
                        file_name
                    )

                    s3_storage = S3Storage()

                    if not s3_storage.exists(file_path_within_bucket):  # avoid overwriting existing file
                        s3_storage.save(file_path_within_bucket, file)
                        s3_file_url = s3_storage.url(file_path_within_bucket)
                    else:
                        raise SingleMessageValidationException(error_500_json())

                    resource.data = {'url': s3_file_url}
                    resource.save()

                return Response(ResourceSerializer(resource).data, status=201)

        except ValidationException as e:
            return Response(status=400, data=e.errors)
        except SingleMessageValidationException as e:
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


class EvaluationResourceViewSet(ViewSet):

    def create(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_READING):
            return Response(status=400, data=error_400_json())

        create_data = request.data.copy()
        evaluation_resource_type = create_data.get('type')
        evaluated_user_key = create_data.get('evaluated_user', None)
        evaluated_group_key = create_data.get('evaluated_group', None)
        resource_data = create_data.get('data', [])
        if type(resource_data) == list:
            return Response(status=400, data=error_400_json())

        create_data["ngo"] = request.user.ngo.key
        create_data["user"] = request.user.key
        if evaluation_resource_type == EvaluationResource.USER:
            try:
                evaluated_user = User.objects.get(key=evaluated_user_key, ngo=request.user.ngo)
            except User.DoesNotExist:
                return Response(status=400)

            create_data["evaluated_user"] = evaluated_user.key
            serializer = EvaluationResourceUserWriteOnlySerializer(data=create_data)
        elif evaluation_resource_type == EvaluationResource.GROUP:
            try:
                evaluated_group = UserGroup.objects.get(key=evaluated_group_key, ngo=request.user.ngo)
            except User.DoesNotExist:
                return Response(status=400)

            create_data["evaluated_group"] = evaluated_group.key
            serializer = EvaluationResourceGroupWriteOnlySerializer(data=create_data)
        else:
            return Response(status=400, data=error_400_json())

        resource_data = json.loads(resource_data)
        create_data["data"] = resource_data
        try:
            if not serializer.is_valid():
                raise ValidationException(serializer.errors)
            evaluation_resource = serializer.save()
            return Response(EvaluationResourceDetailSerializer(evaluation_resource).data, status=201)

        except ValidationException as e:
            return Response(status=400, data=e.errors)

    def update(self, request, pk=None):
        try:
            evaluation_resource = EvaluationResource.objects.get(key=pk)
        except EvaluationResource.DoesNotExist:
            return Response(status=404)

        if not has_permission(request, PERMISSION_CAN_ADD_READING):
            return Response(status=400, data=error_400_json())

        resource_data = request.data.get('data', [])
        is_evaluated = request.data.get('is_evaluated', None)

        if type(resource_data) == list:
            return Response(status=400, data=error_400_json())

        resource_data = json.loads(resource_data)
        evaluation_resource.data = resource_data
        evaluation_resource.is_evaluated = is_evaluated
        evaluation_resource.save()

        serializer = EvaluationResourceDetailSerializer(evaluation_resource)
        return Response(serializer.data)
