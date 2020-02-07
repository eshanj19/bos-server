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

from bos.constants import MESSAGE_KEY
from django.utils.translation import gettext as _

from users.models import UserHierarchy, User
from users.serializers import UserHierarchyReadSerializer, UserHierarchySerializer, UserRestrictedDetailSerializer


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
    available_resource_filters = ['is_active', 'type']
    available_resource_search_filters = ['label']

    for available_resource_filter in available_resource_filters:
        if available_resource_filter in request_data:
            value = request_data.get(available_resource_filter)
            if available_resource_filter == 'is_active':
                if value.lower() == 'false':
                    resource_filter[available_resource_filter] = False
                else:
                    resource_filter[available_resource_filter] = True
            elif available_resource_filter == 'type':
                resource_filter[available_resource_filter] = value

    search_filter = Q()
    for available_resource_search_filter in available_resource_search_filters:
        if available_resource_search_filter in request_data:
            value = request_data.get(available_resource_search_filter)
            if available_resource_search_filter == 'label':
                search_filter = Q(label__icontains=value)

    return resource_filter, search_filter


def user_group_filters_from_request(request_data):
    user_group_filter = {}
    available_user_group_filters = ['is_active']
    available_user_group_search_filters = ['label']

    for available_user_group_filter in available_user_group_filters:
        if available_user_group_filter in request_data:
            value = request_data.get(available_user_group_filter)
            if value.lower() == 'false':
                user_group_filter[available_user_group_filter] = False
            else:
                user_group_filter[available_user_group_filter] = True

    search_filter = Q()
    for available_user_group_search_filter in available_user_group_search_filters:
        if available_user_group_search_filter in request_data:
            value = request_data.get(available_user_group_search_filter)
            if available_user_group_search_filter == 'label':
                search_filter = Q(label__icontains=value)

    return user_group_filter, search_filter


def user_reading_filters_from_request(request_data):
    user_reading_filter = {}
    available_user_reading_filters = ['is_active']
    available_user_reading_search_filters = ['measurement','athlete']

    for available_user_reading_filter in available_user_reading_filters:
        if available_user_reading_filter in request_data:
            value = request_data.get(available_user_reading_filter)
            if value.lower() == 'false':
                user_reading_filter[available_user_reading_filter] = False
            else:
                user_reading_filter[available_user_reading_filter] = True

    search_filter = Q()
    for available_user_reading_search_filter in available_user_reading_search_filters:
        if available_user_reading_search_filter in request_data:
            value = request_data.get(available_user_reading_search_filter)
            if available_user_reading_search_filter == 'athlete':
                search_filter = search_filter & (Q(user__first_name__icontains=value) | Q(user__last_name__icontains=value))
            if available_user_reading_search_filter == 'measurement':
                search_filter = search_filter & Q(measurement__key=value)

    return user_reading_filter, search_filter


def user_request_filters_from_request(request_data):
    user_request_filter = {}
    available_user_reading_filters = ['is_active']
    available_user_request_search_filters = ['first_name']

    for available_user_request_filter in available_user_reading_filters:
        if available_user_request_filter in request_data:
            value = request_data.get(available_user_request_filter)
            if value.lower() == 'false':
                user_request_filter[available_user_request_filter] = False
            else:
                user_request_filter[available_user_request_filter] = True

    search_filter = Q()
    for available_user_request_search_filter in available_user_request_search_filters:
        if available_user_request_search_filter in request_data:
            value = request_data.get(available_user_request_search_filter)
            if available_user_request_search_filter == 'first_name':
                search_filter = search_filter & (Q(user__first_name__icontains=value) | Q(user__last_name__icontains=value))

    return user_request_filter, search_filter


def convert_validation_error_into_response_error(validation_error):
    return {'password': validation_error}

def error_checkone(message):
    return {MESSAGE_KEY:_(message)}


def error_400_json():
    return {MESSAGE_KEY: _('ERROR_MESSAGE_400')}


def error_403_json():
    return {MESSAGE_KEY: _('ERROR_MESSAGE_403')}


def request_status(message):
    return {MESSAGE_KEY:_(message)}


def error_404_json():
    return {MESSAGE_KEY: _('ERROR_MESSAGE_404')}


def error_500_json():
    return {MESSAGE_KEY: _('ERROR_MESSAGE_500')}


def request_user_belongs_to_ngo(request, ngo):
    if request.user and request.user.ngo and request.user.ngo.key == ngo.key:
        return True
    return False


def request_user_belongs_to_user_ngo(request, user):
    if request.user and request.user.ngo and request.user.ngo.key == user.ngo.key:
        return True
    return False


def request_user_belongs_to_user_group_ngo(request, user_group):
    if request.user and request.user.ngo and request.user.ngo.key == user_group.ngo.key:
        return True
    return False


def request_user_belongs_to_resource(request, resource):
    if request.user and request.user.ngo and request.user.ngo.key == resource.ngo.key:
        return True
    return False


def request_user_belongs_to_reading(request, reading):
    if request.user and request.user.ngo and request.user.ngo.key == reading.ngo.key:
        return True
    return False


def request_user_belongs_to_user_request_ngo(request, user_request):
    if request.user and request.user.ngo and request.user.ngo.key == user_request.ngo.key:
        return True
    return False


def find_athletes_under_user(user):
    user_ids = find_user_ids_under_users([user.id], [])
    queryset = User.objects.filter(id__in=user_ids, role=User.ATHLETE)
    serializer = UserRestrictedDetailSerializer(queryset, many=True)
    return serializer.data


def find_user_ids_under_users(user_ids, previous_children):
    children = []
    queryset = UserHierarchy.objects.filter(parent_user__in=user_ids)
    serializer = UserHierarchySerializer(queryset, many=True)
    for child in serializer.data:
        children.append(child['child_user'])
    if len(children) == 0:
        return previous_children
    else:
        return find_user_ids_under_users(children, previous_children + children)
