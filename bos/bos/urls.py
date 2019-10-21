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

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from measurements import views as measurement_views
from ngos import views as ngo_views
from users import views as user_views
from resources import views as resource_views

router = routers.SimpleRouter()
router.register(r'users', user_views.UserViewSet, base_name='users')
router.register(r'admins', user_views.AdminViewSet, base_name='admins')
router.register(r'athletes', user_views.AthleteViewSet, base_name='athletes')
router.register(r'coaches', user_views.CoachViewSet, base_name='coaches')
router.register(r'user_groups', user_views.UserGroupViewSet, base_name='user_groups')
router.register(r'ngos', ngo_views.NGOViewSet, 'NGO')
router.register(r'ping', ngo_views.PingViewSet, 'Ping')
router.register(r'measurements', measurement_views.MeasurementViewSet, 'Measurement')
router.register(r'measurement_types', measurement_views.MeasurementTypeViewSet, 'MeasurementType')
router.register(r'permission_groups', user_views.PermissionGroupViewSet, 'PermissionGroup')
router.register(r'resources', resource_views.ResourceViewSet, 'Resource')

urlpatterns = [
    url(r'^', include(router.urls)),
    path('admin/', admin.site.urls),
    url(r'^login', user_views.login_view, name='login'),
    url(r'^logout', user_views.logout_view, name='logout'),
]

