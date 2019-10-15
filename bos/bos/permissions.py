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

from rest_framework import permissions

# BOS_ADMIN
PERMISSION_BOS_ADMIN = ('bos_admin', 'bos admin', 'users.bos_admin')

# MEASUREMENT
PERMISSION_CAN_ADD_MEASUREMENT = ('add_measurement', 'Can add measurement', 'measurements.add_measurement')
PERMISSION_CAN_CHANGE_MEASUREMENT = ('change_measurement', 'Can change measurement', 'measurements.change_measurement')
PERMISSION_CAN_DESTROY_MEASUREMENT = ('delete_measurement', 'Can delete measurement', 'measurements.delete_measurement')
PERMISSION_CAN_VIEW_MEASUREMENT = ('view_measurement', 'Can view measurement', 'measurements.view_measurement')
PERMISSIONS_MEASUREMENT = [PERMISSION_CAN_ADD_MEASUREMENT, PERMISSION_CAN_CHANGE_MEASUREMENT,
                           PERMISSION_CAN_DESTROY_MEASUREMENT,
                           PERMISSION_CAN_VIEW_MEASUREMENT]

# MEASUREMENT_TYPES
PERMISSION_CAN_ADD_MEASUREMENT_TYPE = (
'add_measurementtype', 'Can add measurement type', 'measurements.add_measurementtype')
PERMISSION_CAN_CHANGE_MEASUREMENT_TYPE = (
    'change_measurementtype', 'Can change measurement type', 'measurements.change_measurementtype')
PERMISSION_CAN_DESTROY_MEASUREMENT_TYPE = (
    'delete_measurementtype', 'Can delete measurement type', 'measurements.delete_measurementtype')
PERMISSION_CAN_VIEW_MEASUREMENT_TYPE = (
    'view_measurementtype', 'Can view measurement type', 'measurements.view_measurementtype')
PERMISSIONS_MEASUREMENT_TYPE = [PERMISSION_CAN_ADD_MEASUREMENT_TYPE, PERMISSION_CAN_CHANGE_MEASUREMENT_TYPE,
                                PERMISSION_CAN_DESTROY_MEASUREMENT_TYPE,
                                PERMISSION_CAN_VIEW_MEASUREMENT_TYPE]

# PERMISSIONS
PERMISSION_CAN_ADD_PERMISSION = ('add_permission', 'Can add permission', 'users.add_permission')
PERMISSION_CAN_CHANGE_PERMISSION = ('change_permission', 'Can change permission', 'users.change_permission')
PERMISSION_CAN_DESTROY_PERMISSION = ('delete_permission', 'Can delete permission', 'users.delete_permission')
PERMISSION_CAN_VIEW_PERMISSION = ('view_permission', 'Can view permission', 'users.view_permission')
PERMISSIONS_PERMISSION = [PERMISSION_CAN_ADD_PERMISSION, PERMISSION_CAN_CHANGE_PERMISSION,
                          PERMISSION_CAN_DESTROY_PERMISSION,
                          PERMISSION_CAN_VIEW_PERMISSION]
# USERS
PERMISSION_CAN_ADD_USER = ('add_user', 'Can add user', 'users.add_user')
PERMISSION_CAN_CHANGE_USER = ('change_user', 'Can change user', 'users.change_user')
PERMISSION_CAN_DESTROY_USER = ('delete_user', 'Can delete user', 'users.delete_user')
PERMISSION_CAN_VIEW_USER = ('view_user', 'Can view user', 'users.view_user')
PERMISSION_CAN_IMPORT_USERS = ('can_import', 'Can import user through excel file', 'users.can_import')
PERMISSION_CAN_EXPORT_USERS = ('can_export', 'Can export user through excel file', 'users.can_export')
PERMISSIONS_USER = [PERMISSION_CAN_ADD_USER, PERMISSION_CAN_CHANGE_USER, PERMISSION_CAN_DESTROY_USER,
                    PERMISSION_CAN_VIEW_USER, PERMISSION_CAN_IMPORT_USERS, PERMISSION_CAN_EXPORT_USERS, ]

# NGOS
PERMISSION_CAN_ADD_NGO = ('add_ngo', 'Can add ngo', 'ngos.add_ngo')
PERMISSION_CAN_CHANGE_NGO = ('change_ngo', 'Can change ngo', 'ngos.change_ngo')
PERMISSION_CAN_DESTROY_NGO = ('delete_ngo', 'Can delete ngo', 'ngos.delete_ngo')
PERMISSION_CAN_VIEW_NGO = ('view_ngo', 'Can view ngo', 'ngos.view_ngo')
PERMISSIONS_NGO = [PERMISSION_CAN_ADD_NGO, PERMISSION_CAN_CHANGE_NGO, PERMISSION_CAN_DESTROY_NGO,
                   PERMISSION_CAN_VIEW_NGO]

DEFAULT_PERMISSIONS_ADMIN = PERMISSIONS_PERMISSION + PERMISSIONS_MEASUREMENT + PERMISSIONS_MEASUREMENT_TYPE
DEFAULT_PERMISSIONS_COACH = []


def has_permission(request, permission):
    if request.user and request.user.has_perm(permission[2]):
        return True
    return False


class CanAddUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_USER)


class CanChangeUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_USER)


class CanDeleteUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_USER)


class CanViewUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_USER)


class CanAddMeasurement(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_MEASUREMENT)


class CanChangeMeasurement(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_MEASUREMENT)


class CanDeleteMeasurement(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_MEASUREMENT)


class CanViewMeasurement(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_MEASUREMENT)


class CanAddMeasurementType(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_MEASUREMENT_TYPE)


class CanChangeMeasurementType(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_MEASUREMENT_TYPE)


class CanDeleteMeasurementType(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_MEASUREMENT_TYPE)


class CanViewMeasurementType(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_MEASUREMENT_TYPE)
