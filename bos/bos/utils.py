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
from django.db.models import Q


def get_ngo_group_name(ngo, name):
    return ngo.key + '_' + name


def user_sort_by_value(sort, order):
    order_by = None
    # if sort == 'first_name':
    #     order_by = 'first_name'
    print(sort, order)
    order_by = sort

    if order == 'ASC':
        return order_by
    if order == 'DESC':
        return '-' + order_by
    return order_by


def user_filters_from_request(request_data):
    user_filter = {}
    available_user_filters = ['is_active']
    available_user_search_filters = ['name']

    for available_user_filter in available_user_filters:
        if available_user_filter in request_data:
            value = request_data.get(available_user_filter)
            if value.lower() == 'false':
                user_filter[available_user_filter] = False
            else:
                user_filter[available_user_filter] = True

    search_filter = Q()
    for available_user_search_filter in available_user_search_filters:
        if available_user_search_filter in request_data:
            value = request_data.get(available_user_search_filter)
            if available_user_search_filter == 'name':
                search_filter = Q(first_name__icontains=value) | Q(last_name__icontains=value)

    return user_filter, search_filter


def measurement_filters_from_request(request_data):
    measurement_filter = {}
    available_measurement_filters = ['is_active', 'types']
    available_measurement_search_filters = ['label']

    for available_measurement_filter in available_measurement_filters:
        if available_measurement_filter in request_data:
            value = request_data.get(available_measurement_filter)
            if available_measurement_filter == 'is_active':
                if value.lower() == 'false':
                    measurement_filter[available_measurement_filter] = False
                else:
                    measurement_filter[available_measurement_filter] = True
            if available_measurement_filter == 'types':
                measurement_filter['types__key'] = value

    search_filter = Q()
    for available_measurement_search_filter in available_measurement_search_filters:
        if available_measurement_search_filter in request_data:
            value = request_data.get(available_measurement_search_filter)
            if available_measurement_search_filter == 'label':
                search_filter = Q(label__icontains=value)

    return measurement_filter, search_filter


def measurement_type_filters_from_request(request_data):
    measurement_type_filter = {}
    available_measurement_type_filters = ['is_active']
    available_measurement_type_search_filters = ['label']

    for available_measurement_type_filter in available_measurement_type_filters:
        if available_measurement_type_filter in request_data:
            value = request_data.get(available_measurement_type_filter)
            if value.lower() == 'false':
                measurement_type_filter[available_measurement_type_filter] = False
            else:
                measurement_type_filter[available_measurement_type_filter] = True

    search_filter = Q()
    for available_measurement_type_search_filter in available_measurement_type_search_filters:
        if available_measurement_type_search_filter in request_data:
            value = request_data.get(available_measurement_type_search_filter)
            if available_measurement_type_search_filter == 'label':
                search_filter = Q(label__icontains=value)

    return measurement_type_filter, search_filter


def ngo_filters_from_request(request_data):
    ngo_filter = {}
    available_ngo_filters = ['is_active']
    available_ngo_search_filters = ['name']

    for available_ngo_filter in available_ngo_filters:
        if available_ngo_filter in request_data:
            value = request_data.get(available_ngo_filter)
            if value.lower() == 'false':
                ngo_filter[available_ngo_filter] = False
            else:
                ngo_filter[available_ngo_filter] = True

    search_filter = Q()
    for available_ngo_search_filter in available_ngo_search_filters:
        if available_ngo_search_filter in request_data:
            value = request_data.get(available_ngo_search_filter)
            if available_ngo_search_filter == 'name':
                search_filter = Q(name__icontains=value)

    return ngo_filter, search_filter


def resource_filters_from_request(request_data):
    resource_filter = {}
    available_resource_filters = ['is_active']
    available_resource_search_filters = ['name']

    for available_resource_filter in available_resource_filters:
        if available_resource_filter in request_data:
            value = request_data.get(available_resource_filter)
            if value.lower() == 'false':
                resource_filter[available_resource_filter] = False
            else:
                resource_filter[available_resource_filter] = True

    search_filter = Q()
    for available_resource_search_filter in available_resource_search_filters:
        if available_resource_search_filter in request_data:
            value = request_data.get(available_resource_search_filter)
            if available_resource_search_filter == 'name':
                search_filter = Q(name__icontains=value)

    return resource_filter, search_filter


