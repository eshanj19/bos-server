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

# CURRICULUM
PERMISSION_CAN_ADD_CURRICULUM = ('add_curriculum', 'Can add curriculum', 'resources.add_curriculum')
PERMISSION_CAN_CHANGE_CURRICULUM = ('change_curriculum', 'Can change curriculum', 'resources.change_curriculum')
PERMISSION_CAN_DESTROY_CURRICULUM = ('delete_curriculum', 'Can delete curriculum', 'resources.delete_curriculum')
PERMISSION_CAN_VIEW_CURRICULUM = ('view_curriculum', 'Can view curriculum', 'resources.view_curriculum')
PERMISSIONS_CURRICULUM = [PERMISSION_CAN_ADD_CURRICULUM, PERMISSION_CAN_CHANGE_CURRICULUM,
                          PERMISSION_CAN_DESTROY_CURRICULUM,
                          PERMISSION_CAN_VIEW_CURRICULUM]
# RESOURCES
PERMISSION_CAN_ADD_RESOURCE = ('add_resource', 'Can add resource', 'resources.add_resource')
PERMISSION_CAN_CHANGE_RESOURCE = ('change_resource', 'Can change resource', 'resources.change_resource')
PERMISSION_CAN_DESTROY_RESOURCE = ('delete_resource', 'Can delete resource', 'resources.delete_resource')
PERMISSION_CAN_VIEW_RESOURCE = ('view_resource', 'Can view resource', 'resources.view_resource')
PERMISSIONS_RESOURCE = [PERMISSION_CAN_ADD_RESOURCE, PERMISSION_CAN_CHANGE_RESOURCE, PERMISSION_CAN_DESTROY_RESOURCE,
                        PERMISSION_CAN_VIEW_RESOURCE]

# TRAINING_SESSION
PERMISSION_CAN_ADD_TRAINING_SESSION = ('add_trainingsession', 'Can add session', 'resources.add_trainingsession')
PERMISSION_CAN_CHANGE_TRAINING_SESSION = (
    'change_trainingsession', 'Can change session', 'resources.change_trainingsession')
PERMISSION_CAN_DESTROY_TRAINING_SESSION = (
    'delete_trainingsession', 'Can delete session', 'resources.delete_trainingsession')
PERMISSION_CAN_VIEW_TRAINING_SESSION = ('view_trainingsession', 'Can view session', 'resources.view_trainingsession')
PERMISSIONS_TRAINING_SESSION = [PERMISSION_CAN_ADD_TRAINING_SESSION, PERMISSION_CAN_CHANGE_TRAINING_SESSION,
                                PERMISSION_CAN_DESTROY_TRAINING_SESSION,
                                PERMISSION_CAN_VIEW_TRAINING_SESSION]

# FILE
PERMISSION_CAN_ADD_FILE = ('add_file', 'Can add file', 'resources.add_file')
PERMISSION_CAN_CHANGE_FILE = ('change_file', 'Can change file', 'resources.change_file')
PERMISSION_CAN_DESTROY_FILE = ('delete_file', 'Can delete file', 'resources.delete_file')
PERMISSION_CAN_VIEW_FILE = ('view_file', 'Can view file', 'files.view_file')
PERMISSIONS_FILE = [PERMISSION_CAN_ADD_FILE, PERMISSION_CAN_CHANGE_FILE,
                    PERMISSION_CAN_DESTROY_FILE,
                    PERMISSION_CAN_VIEW_FILE]

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

# ADMINS
PERMISSION_CAN_ADD_ADMIN = ('add_admin', 'Can add admin', 'users.add_admin')
PERMISSION_CAN_CHANGE_ADMIN = ('change_admin', 'Can change admin', 'users.change_admin')
PERMISSION_CAN_DESTROY_ADMIN = ('delete_admin', 'Can delete admin', 'users.delete_admin')
PERMISSION_CAN_VIEW_ADMIN = ('view_admin', 'Can view admin', 'users.view_admin')
PERMISSIONS_ADMIN = [PERMISSION_CAN_ADD_ADMIN, PERMISSION_CAN_CHANGE_ADMIN, PERMISSION_CAN_DESTROY_ADMIN,
                     PERMISSION_CAN_VIEW_ADMIN, ]

# ATHLETES
PERMISSION_CAN_ADD_ATHLETE = ('add_athlete', 'Can add athlete', 'users.add_athlete')
PERMISSION_CAN_CHANGE_ATHLETE = ('change_athlete', 'Can change athlete', 'users.change_athlete')
PERMISSION_CAN_DESTROY_ATHLETE = ('delete_athlete', 'Can delete athlete', 'users.delete_athlete')
PERMISSION_CAN_VIEW_ATHLETE = ('view_athlete', 'Can view athlete', 'users.view_athlete')
PERMISSIONS_ATHLETE = [PERMISSION_CAN_ADD_ATHLETE, PERMISSION_CAN_CHANGE_ATHLETE, PERMISSION_CAN_DESTROY_ATHLETE,
                       PERMISSION_CAN_VIEW_ATHLETE, ]

# COACHES
PERMISSION_CAN_ADD_COACH = ('add_coach', 'Can add coach', 'users.add_coach')
PERMISSION_CAN_CHANGE_COACH = ('change_coach', 'Can change coach', 'users.change_coach')
PERMISSION_CAN_DESTROY_COACH = ('delete_coach', 'Can delete coach', 'users.delete_coach')
PERMISSION_CAN_VIEW_COACH = ('view_coach', 'Can view coach', 'users.view_coach')
PERMISSIONS_COACH = [PERMISSION_CAN_ADD_COACH, PERMISSION_CAN_CHANGE_COACH, PERMISSION_CAN_DESTROY_COACH,
                     PERMISSION_CAN_VIEW_COACH, ]

# NGOS
PERMISSION_CAN_ADD_NGO = ('add_ngo', 'Can add ngo', 'ngos.add_ngo')
PERMISSION_CAN_CHANGE_NGO = ('change_ngo', 'Can change ngo', 'ngos.change_ngo')
PERMISSION_CAN_DESTROY_NGO = ('delete_ngo', 'Can delete ngo', 'ngos.delete_ngo')
PERMISSION_CAN_VIEW_NGO = ('view_ngo', 'Can view ngo', 'ngos.view_ngo')
PERMISSIONS_NGO = [PERMISSION_CAN_ADD_NGO, PERMISSION_CAN_CHANGE_NGO, PERMISSION_CAN_DESTROY_NGO,
                   PERMISSION_CAN_VIEW_NGO]

# CUSTOM_USER_GROUPS
PERMISSION_CAN_ADD_CUSTOM_USER_GROUP = ('add_customusergroup', 'Can add custom user group', 'users.add_customusergroup')
PERMISSION_CAN_CHANGE_CUSTOM_USER_GROUP = (
    'change_customusergroup', 'Can change custom user group', 'users.change_customusergroup')
PERMISSION_CAN_DESTROY_CUSTOM_USER_GROUP = (
    'delete_customusergroup', 'Can delete custom user group', 'users.delete_customusergroup')
PERMISSION_CAN_VIEW_CUSTOM_USER_GROUP = (
    'view_customusergroup', 'Can view custom user group', 'users.view_customusergroup')
PERMISSIONS_CUSTOM_USER_GROUP = [PERMISSION_CAN_ADD_CUSTOM_USER_GROUP, PERMISSION_CAN_CHANGE_CUSTOM_USER_GROUP,
                                 PERMISSION_CAN_DESTROY_CUSTOM_USER_GROUP,
                                 PERMISSION_CAN_VIEW_CUSTOM_USER_GROUP]

# PERMISSION_GROUPS
PERMISSION_CAN_ADD_PERMISSION_GROUP = ('add_permissiongroup', 'Can add permissiongroup', 'users.add_permissiongroup')
PERMISSION_CAN_CHANGE_PERMISSION_GROUP = (
    'change_permissiongroup', 'Can change permissiongroup', 'users.change_permissiongroup')
PERMISSION_CAN_DESTROY_PERMISSION_GROUP = (
    'delete_permissiongroup', 'Can delete permissiongroup', 'users.delete_permissiongroup')
PERMISSION_CAN_VIEW_PERMISSION_GROUP = (
    'view_permissiongroup', 'Can view permissiongroup', 'users.view_permissiongroup')
PERMISSIONS_PERMISSION_GROUP = [PERMISSION_CAN_ADD_PERMISSION_GROUP, PERMISSION_CAN_CHANGE_PERMISSION_GROUP,
                                PERMISSION_CAN_DESTROY_PERMISSION_GROUP,
                                PERMISSION_CAN_VIEW_PERMISSION_GROUP]

DEFAULT_PERMISSIONS_NGO_ADMIN = PERMISSIONS_PERMISSION + PERMISSIONS_MEASUREMENT + PERMISSIONS_MEASUREMENT_TYPE + \
                                PERMISSIONS_RESOURCE + PERMISSIONS_CURRICULUM + PERMISSIONS_FILE + \
                                PERMISSIONS_TRAINING_SESSION + PERMISSIONS_COACH + PERMISSIONS_ATHLETE + \
                                PERMISSIONS_ADMIN + PERMISSIONS_CUSTOM_USER_GROUP + PERMISSIONS_PERMISSION_GROUP

DEFAULT_PERMISSIONS_BOS_NGO_ADMIN = PERMISSIONS_NGO + DEFAULT_PERMISSIONS_NGO_ADMIN


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


class CanAddAthlete(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_ATHLETE)


class CanChangeAthlete(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_ATHLETE)


class CanDeleteAthlete(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_ATHLETE)


class CanViewAthlete(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_ATHLETE)


class CanAddAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_ADMIN)


class CanChangeAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_ADMIN)


class CanDeleteAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_ADMIN)


class CanViewAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_ADMIN)


class CanAddCoach(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_COACH)


class CanChangeCoach(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_COACH)


class CanDeleteCoach(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_COACH)


class CanViewCoach(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_COACH)


class CanAddCustomUserGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_CUSTOM_USER_GROUP)


class CanChangeCustomUserGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_CUSTOM_USER_GROUP)


class CanDeleteCustomUserGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_CUSTOM_USER_GROUP)


class CanViewCustomUserGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_CUSTOM_USER_GROUP)


class CanAddFile(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_FILE)


class CanChangeFile(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_FILE)


class CanDeleteFile(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_FILE)


class CanViewFile(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_FILE)


class CanAddTrainingSession(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_TRAINING_SESSION)


class CanChangeTrainingSession(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_TRAINING_SESSION)


class CanDeleteTrainingSession(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_TRAINING_SESSION)


class CanViewTrainingSession(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_TRAINING_SESSION)


class CanAddCurriculum(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_CURRICULUM)


class CanChangeCurriculum(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_CURRICULUM)


class CanDeleteCurriculum(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_CURRICULUM)


class CanViewCurriculum(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_CURRICULUM)


class CanAddPermissionGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_ADD_PERMISSION_GROUP)


class CanChangePermissionGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_CHANGE_PERMISSION_GROUP)


class CanDeletePermissionGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_DESTROY_PERMISSION_GROUP)


class CanViewPermissionGroup(permissions.BasePermission):

    def has_permission(self, request, view):
        return has_permission(request, PERMISSION_CAN_VIEW_PERMISSION_GROUP)
