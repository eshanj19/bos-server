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
import requests
from django.core.management import BaseCommand

from ngos.models import NGO
from users.management.commands.superset_api import login_superset, get_users, get_roles, update_superset_user_if_needed, \
    create_superset_user, create_ngo_role_if_needed, create_ngo_table_if_needed, create_bos_database_if_needed, \
    get_databases, find_bos_database_from_superset_databases, find_user, find_ngo_role_from_superset_roles, \
    find_gamma_role_from_superset_roles
from users.models import User


def _process_ngo(self, ngo, superset_users, superset_role, session):
    # fetch admin users for the ngo
    admin_users = User.objects.filter(role=User.ADMIN, ngo=ngo)
    for admin_user in admin_users:
        # update_superset_user_password(self,admin_user,session)
        superset_user = find_user(admin_user, superset_users)
        if superset_user:
            self.stdout.write(self.style.SUCCESS('Superset user exists'))
            # Check if superset user is active
            update_superset_user_if_needed(admin_user, superset_user, superset_role, session)
        else:
            create_superset_user(admin_user, superset_role, session)


def _superset_init(self):
    ngos = NGO.objects.filter(is_active=True)
    with requests.Session() as session:
        session.auth = ('user', 'pass')
        # Login in as admin
        if not login_superset(session):
            return

        # Check if bos database created in superset database
        is_successful, superset_databases = get_databases(session)
        if not is_successful:
            return False

        is_successful = create_bos_database_if_needed(session)
        if not is_successful:
            return

        superset_bos_database = find_bos_database_from_superset_databases(superset_databases)
        if not superset_bos_database:
            return False

        # Check if tables are created for all the ngos
        is_successful = create_ngo_table_if_needed(ngos, superset_bos_database, session)
        if not is_successful:
            return

        # Check if permissions are created for all the ngos
        is_successful = create_ngo_role_if_needed(ngos, session)
        if not is_successful:
            return
        # Fetch all users in superset
        is_successful, superset_users = get_users(session)
        if not is_successful:
            return
        is_successful, superset_roles = get_roles(session)
        if not is_successful:
            return
        for ngo in ngos:
            superset_role = find_ngo_role_from_superset_roles(ngo, superset_roles)
            gamma_superset_role = find_gamma_role_from_superset_roles(superset_roles)
            assert gamma_superset_role
            _process_ngo(self, ngo, superset_users, [superset_role, gamma_superset_role], session)


class Command(BaseCommand):
    help = 'Create superset users for superset'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        _superset_init(self)
        print("Finished")
        return
