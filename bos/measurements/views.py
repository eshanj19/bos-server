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
from psycopg2._psycopg import DatabaseError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.utils.translation import gettext as _

from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.permissions import has_permission, PERMISSION_CAN_VIEW_MEASUREMENT, PERMISSION_CAN_ADD_MEASUREMENT, \
    PERMISSION_CAN_CHANGE_MEASUREMENT, PERMISSION_CAN_DESTROY_MEASUREMENT, PERMISSION_CAN_VIEW_MEASUREMENT_TYPE, \
    PERMISSION_CAN_ADD_MEASUREMENT_TYPE, PERMISSION_CAN_CHANGE_MEASUREMENT_TYPE, PERMISSION_CAN_DESTROY_MEASUREMENT_TYPE
from bos.utils import measurement_filters_from_request, measurement_type_filters_from_request
from measurements.models import Measurement, MeasurementType
from measurements.serializers import MeasurementSerializer, MeasurementTypeSerializer


class MeasurementViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_MEASUREMENT):
            return Response(status=403)

        measurement_filters, search_filters = measurement_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
        }
        filters = {**common_filters, **measurement_filters}

        queryset = Measurement.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = MeasurementSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_MEASUREMENT):
            return Response(status=403)

        create_data = request.data
        create_data['ngo'] = request.user.ngo.key
        try:
            with transaction.atomic():
                serializer = MeasurementSerializer(data=create_data)
                if not serializer.is_valid():
                    raise ValidationException(serializer.errors)
                serializer.save()
                return Response(serializer.data, status=201)

        except DatabaseError:
            return Response(status=500)
        except ValidationException as e:
            return Response(e.errors, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_MEASUREMENT):
            return Response(status=403)
        queryset = Measurement.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = MeasurementSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_MEASUREMENT):
            return Response(status=403)

        try:
            item = Measurement.objects.get(key=pk)
        except Measurement.DoesNotExist:
            return Response(status=404)
        serializer = MeasurementSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_MEASUREMENT):
            return Response(status=403)

        try:
            item = Measurement.objects.get(key=pk)
        except Measurement.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)




class MeasurementTypeViewSet(ViewSet):

    def list(self, request):
        if not has_permission(request, PERMISSION_CAN_VIEW_MEASUREMENT_TYPE):
            return Response(status=403)

        measurement_type_filters, search_filters = measurement_type_filters_from_request(request.GET)
        ordering = request.GET.get('ordering', None)
        common_filters = {
            'ngo': request.user.ngo,
        }
        filters = {**common_filters, **measurement_type_filters}

        queryset = MeasurementType.objects.filter(search_filters, **filters)
        if ordering:
            queryset = queryset.order_by(ordering)
        paginator = BOSPageNumberPagination()
        result = paginator.paginate_queryset(queryset, request)
        serializer = MeasurementTypeSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        if not has_permission(request, PERMISSION_CAN_ADD_MEASUREMENT_TYPE):
            return Response(status=403)

        create_data = request.data
        create_data['ngo'] = request.user.ngo.key
        serializer = MeasurementTypeSerializer(data=create_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_VIEW_MEASUREMENT_TYPE):
            return Response(status=403)

        queryset = MeasurementType.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = MeasurementTypeSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_CHANGE_MEASUREMENT_TYPE):
            return Response(status=403)

        try:
            item = MeasurementType.objects.get(key=pk)
        except MeasurementType.DoesNotExist:
            return Response(status=404)
        serializer = MeasurementTypeSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        if not has_permission(request, PERMISSION_CAN_DESTROY_MEASUREMENT_TYPE):
            return Response(status=403)

        try:
            item = MeasurementType.objects.get(key=pk)
        except MeasurementType.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)
