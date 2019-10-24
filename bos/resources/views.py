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
from django.shortcuts import render, get_object_or_404

# Create your views here.
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from bos.constants import METHOD_POST
from bos.exceptions import ValidationException
from bos.pagination import BOSPageNumberPagination
from bos.utils import resource_filters_from_request
from resources.models import Resource
from resources.serializers import ResourceSerializer
from rest_framework.response import Response


class ResourceViewSet(ViewSet):

    def list(self, request):
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
        print(create_data)
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
        queryset = Resource.objects.all()
        item = get_object_or_404(queryset, key=pk)
        serializer = ResourceSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Resource.objects.get(key=pk)
        except Resource.DoesNotExist:
            return Response(status=404)

        if request.user.ngo != item.ngo:
            return Response(status=400)

        update_data = request.data.copy()
        update_data['ngo'] = request.user.ngo.key
        serializer = ResourceSerializer(item, data=update_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Resource.objects.get(key=pk)
        except Resource.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

    @action(detail=True,methods=[METHOD_POST])
    def deactivate(self, request, pk=None):
        ngo = request.user.ngo
        try:
            item = Resource.objects.get(key=pk,ngo=ngo)
        except Resource.DoesNotExist:
            return Response(status=404)
        item.is_active = False
        item.save()
        return Response(status=204)

    @action(detail=True,methods=[METHOD_POST])
    def activate(self, request, pk=None):
        ngo = request.user.ngo
        try:
            item = Resource.objects.get(key=pk, ngo=ngo)
        except Resource.DoesNotExist:
            return Response(status=404)
        item.is_active = True
        item.save()
        return Response(status=204)

