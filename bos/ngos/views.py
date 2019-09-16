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

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import pagination
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from bos.defaults import DEFAULT_MEASUREMENT_TYPES
from measurements.models import generate_measurement_key
from measurements.serializers import MeasurementTypeSerializer
from ngos.serializers import NGOSerializer, ResourceTemplateSerializer, ResourceFileSerializer
from ngos.models import NGO, ResourceTemplate, ResourceFile


class NGOViewSet(ViewSet):

    def list(self, request):

        queryset = NGO.objects.all()
        paginator = pagination.PageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = NGOSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        # TODO
        serializer = NGOSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            with transaction.atomic():
                ngo = serializer.save()
                for measurement_type in DEFAULT_MEASUREMENT_TYPES:
                    measurement_type_data = {"key": generate_measurement_key, "label": measurement_type,
                                             "ngo": ngo.key, "is_active": True}
                serializer = MeasurementTypeSerializer(data=measurement_type_data)
                if serializer.is_valid():
                    serializer.save()

                return Response(serializer.data, status=201)
        except Exception:
            return Response(status=500)

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


class ResourceTemplateViewSet(ViewSet):

    def list(self, request):
        queryset = ResourceTemplate.objects.all()
        serializer = ResourceTemplateSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ResourceTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = ResourceTemplate.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ResourceTemplateSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = ResourceTemplate.objects.get(pk=pk)
        except ResourceTemplate.DoesNotExist:
            return Response(status=404)
        serializer = ResourceTemplateSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = ResourceTemplate.objects.get(pk=pk)
        except ResourceTemplate.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ResourceFileViewSet(ViewSet):

    def list(self, request):
        queryset = ResourceFile.objects.all()
        serializer = ResourceFileSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ResourceFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = ResourceFile.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ResourceFileSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = ResourceFile.objects.get(pk=pk)
        except ResourceFile.DoesNotExist:
            return Response(status=404)
        serializer = ResourceFileSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = ResourceFile.objects.get(pk=pk)
        except ResourceFile.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)
