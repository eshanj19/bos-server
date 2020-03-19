#  Copyright (c) 2020. Maverick Labs
#
#    This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as,
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import base64

import psycopg2
from django.conf import settings

HTTP_URL = "http://192.168.0.122:8088/"
SUPERSET_LOGIN_URL = HTTP_URL + "login/"
SUPERSET_GET_ROLES_URL = HTTP_URL + "roles/api/read"
SUPERSET_GET_TABLES_URL = HTTP_URL + "tablemodelview/api/read"
SUPERSET_GET_DATABASES_URL = HTTP_URL + "databaseview/api/read"
SUPERSET_GET_USERS_URL = HTTP_URL + "users/api/read"
SUPERSET_CREATE_USERS_URL = HTTP_URL + "users/api/create"
SUPERSET_EDIT_USERS_URL = HTTP_URL + "users/edit/%s"
SUPERSET_CREATE_ROLES_URL = HTTP_URL + "roles/api/create"
SUPERSET_CREATE_TABLES_URL = HTTP_URL + "tablemodelview/api/create"
SUPERSET_CREATE_DATABASES_URL = HTTP_URL + "databaseview/api/create"
SUPERSET_DATABASE = "superset"
GAMMA_ROLE = "Gamma"
SUPERSET_BASE_TABLE_NAME = "user_readings_%s"
BASE_DATABASE_CONNECTION_URL = "postgresql+psycopg2://%s:%s@%s/%s"
HTTP_OK = 200

CONFIG_DATABASES = getattr(settings, "DATABASES", None)
BOS_DATABASE_NAME = CONFIG_DATABASES["default"]["NAME"]
BOS_DATABASE_USER = CONFIG_DATABASES["default"]["USER"]
BOS_DATABASE_PASSWORD = CONFIG_DATABASES["default"]["PASSWORD"]
BOS_DATABASE_HOST = CONFIG_DATABASES["default"]["HOST"]
BOS_DATABASE_CONNECTION_URL = BASE_DATABASE_CONNECTION_URL % (BOS_DATABASE_USER, BOS_DATABASE_PASSWORD,
                                                              BOS_DATABASE_HOST, BOS_DATABASE_NAME)

SUPERSET_DATABASE_CONNECTION_URL = BASE_DATABASE_CONNECTION_URL % (BOS_DATABASE_USER, BOS_DATABASE_PASSWORD,
                                                                   BOS_DATABASE_HOST, SUPERSET_DATABASE)


def find_user(admin_user, superset_users):
    for superset_user in superset_users:
        if admin_user.username == superset_user.username:
            return superset_user
    return None


def find_ngo_role_from_superset_roles(ngo, superset_roles):
    for superset_role in superset_roles:
        if ngo.key == superset_role.name:
            return superset_role
    return None


def find_gamma_role_from_superset_roles(superset_roles):
    for superset_role in superset_roles:
        if GAMMA_ROLE == superset_role.name:
            return superset_role
    return None


def find_ngo_permission_view_from_permission_views(ngo, permission_views):
    for permission_view in permission_views:
        if ngo.key in permission_view.name:
            return permission_view
    return None


def find_ngo_table_from_superset_tables(ngo, superset_tables):
    for superset_table in superset_tables:
        ngo_table_name = SUPERSET_BASE_TABLE_NAME % ngo.key
        # THIS is HACKY
        if ngo_table_name in superset_table.link:
            return superset_table
    return None


def find_bos_database_from_superset_databases(superset_databases):
    for superset_database in superset_databases:
        if BOS_DATABASE_NAME == superset_database.database_name:
            return superset_database
    return None


def get_users(self, session):
    response = session.get(SUPERSET_GET_USERS_URL)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Get users failed'))
        return False, []

    json_data = response.json()
    users_json = json_data.get("result", [])
    users_pks = json_data.get("pks", [])
    superset_users = []
    for index, user_json in enumerate(users_json):
        user_json['pk'] = users_pks[index]
        superset_users.append(SupersetUser.from_json(user_json))
    self.stdout.write(self.style.SUCCESS('Get users successful'))
    return True, superset_users


def get_roles(self, session):
    response = session.get(SUPERSET_GET_ROLES_URL)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Get roles failed'))
        return False, []

    json_data = response.json()
    roles_json = json_data.get("result", [])
    roles_pks = json_data.get("pks", [])
    superset_roles = []
    for index, role_json in enumerate(roles_json):
        role_json['pk'] = roles_pks[index]
        superset_roles.append(SupersetRole.from_json(role_json))
    self.stdout.write(self.style.SUCCESS('Get roles successful'))
    print(superset_roles)
    return True, superset_roles


def get_tables(self, session):
    response = session.get(SUPERSET_GET_TABLES_URL)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Get roles failed'))
        return False, []

    json_data = response.json()
    roles_json = json_data.get("result", [])
    roles_pks = json_data.get("pks", [])
    superset_tables = []
    for index, table_json in enumerate(roles_json):
        table_json['pk'] = roles_pks[index]
        superset_tables.append(SupersetTable.from_json(table_json))
    self.stdout.write(self.style.SUCCESS('Get tables successful'))
    print(superset_tables)
    return True, superset_tables


def get_databases(self, session):
    response = session.get(SUPERSET_GET_DATABASES_URL)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Get databases failed'))
        return False, []

    json_data = response.json()
    databases_json = json_data.get("result", [])
    databases_pks = json_data.get("pks", [])
    superset_databases = []
    for index, database_json in enumerate(databases_json):
        database_json['pk'] = databases_pks[index]
        superset_databases.append(SupersetDatabase.from_json(database_json))
    self.stdout.write(self.style.SUCCESS('Get databases successful'))
    print(superset_databases)
    return True, superset_databases


def is_superset_user_dirty(self, user, superset_user):
    print(user.is_active)
    print(superset_user.active)
    if user.username != superset_user.username:
        self.stdout.write(self.style.SUCCESS('username changed'))
        return True
    if user.first_name != superset_user.first_name:
        self.stdout.write(self.style.SUCCESS('first_name changed'))
        return True
    if user.last_name != superset_user.last_name:
        self.stdout.write(self.style.SUCCESS('last_name changed'))
        return True
    if user.is_active != superset_user.active:
        self.stdout.write(self.style.SUCCESS('active changed'))
        return True
    if user.email != superset_user.email:
        self.stdout.write(self.style.SUCCESS('email changed'))
        return True
    return False


def create_role(self, ngo, permission_view, session):
    create_data = {"name": ngo.key,
                   "permissions": [permission_view.pk]}
    print(create_data)
    response = session.post(SUPERSET_CREATE_ROLES_URL, data=create_data)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Create role failed'))
        return False
    self.stdout.write(self.style.SUCCESS('Create role successful'))
    print(response.json())
    return True


def create_table(self, ngo, superset_bos_database, session):
    ngo_table_name = SUPERSET_BASE_TABLE_NAME % ngo.key
    create_data = {"database": superset_bos_database.pk,
                   "table_name": ngo_table_name}
    response = session.post(SUPERSET_CREATE_TABLES_URL, data=create_data)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Create table failed'))
        print(response.json())
        return False
    self.stdout.write(self.style.SUCCESS('Create table successful'))
    print(response.json())
    return True


def create_bos_database(self, session):
    create_data = {"database_name": BOS_DATABASE_NAME,
                   "sqlalchemy_uri": BOS_DATABASE_CONNECTION_URL,
                   "expose_in_sqllab": True,
                   }
    response = session.post(SUPERSET_CREATE_DATABASES_URL, data=create_data)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Create bos database failed'))
        print(response)
        return False
    self.stdout.write(self.style.SUCCESS('Create bos database successful'))
    print(response.json())
    return True


def create_ngo_role_if_needed(self, ngos, session):
    is_successful, superset_roles = get_roles(self, session)
    if not is_successful:
        return False

    query_string = "SELECT abpv.id,abvm.name from ab_permission_view abpv,ab_view_menu abvm,ab_permission abp WHERE " \
                   "abpv.view_menu_id=abvm.id AND abpv.permission_id=abp.id AND abp.name='datasource_access'; "
    is_successful, permission_view_rows = execute_raw_query(query_string, True)
    if not is_successful:
        return False

    permission_views = []
    for permission_view in permission_view_rows:
        permission_views.append(SupersetPermissionView.from_tuple(permission_view))

    for ngo in ngos:
        superset_role = find_ngo_role_from_superset_roles(ngo, superset_roles)
        if not superset_role:
            permission_view = find_ngo_permission_view_from_permission_views(ngo, permission_views)

            is_successful = create_role(self, ngo, permission_view, session)
            if not is_successful:
                return False
    return True


def create_ngo_table_if_needed(self, ngos, superset_bos_database, session):
    is_successful, superset_tables = get_tables(self, session)
    if not is_successful:
        return False

    for ngo in ngos:
        superset_table = find_ngo_table_from_superset_tables(ngo, superset_tables)
        if not superset_table:
            is_successful = create_table(self, ngo, superset_bos_database, session)
            if not is_successful:
                return False
    return True


def create_bos_database_if_needed(self, session):
    is_successful, superset_databases = get_databases(self, session)
    if not is_successful:
        return False

    superset_bos_database = find_bos_database_from_superset_databases(superset_databases)
    if not superset_bos_database:
        is_successful = create_bos_database(self, session)
        if not is_successful:
            return False
    return True


def update_superset_user_password(self, user):
    algorithm, iterations, salt, password_hash = user.password.split('$', 3)
    algorithm = algorithm.replace("_", ":")
    password_hash = base64.b64decode(password_hash).hex()
    superset_password = "%s:%s$%s$%s" % (algorithm, iterations, salt, password_hash)

    query_string = "UPDATE ab_user SET password='%s' WHERE username='%s';" % (superset_password, user.username)
    is_successful, _ = execute_raw_query(query_string, False)
    if not is_successful:
        self.stdout.write(self.style.ERROR('updated password %s') % user.username)
        return False
    print(query_string)
    print(superset_password)
    self.stdout.write(self.style.SUCCESS('Updated password %s') % user.username)
    return True


def update_superset_user_if_needed(self, user, superset_user, superset_roles, session):
    if is_superset_user_dirty(self, user, superset_user):
        update_data = {}
        update_data["first_name"] = user.first_name
        update_data["last_name"] = user.last_name
        update_data["username"] = user.username
        update_data["roles"] = [superset_role.pk for superset_role in superset_roles]
        update_data["email"] = user.email
        update_data["active"] = user.is_active
        # update_data["conf_password"] = "admin@123"
        response = session.post(SUPERSET_EDIT_USERS_URL % superset_user.pk, data=update_data)
        if response.status_code != HTTP_OK:
            self.stdout.write(self.style.ERROR('Update user failed'))
            return False
        self.stdout.write(self.style.SUCCESS('Update user successful'))

    self.stdout.write(self.style.SUCCESS('User is upto date'))

    # update Password for user
    if not update_superset_user_password(self, user):
        self.stdout.write(self.style.ERROR('Update password failed'))
        return False

    return True


def create_superset_user(self, user, superset_roles, session):
    create_data = {}
    create_data["first_name"] = user.first_name
    create_data["last_name"] = user.last_name
    create_data["username"] = user.username
    create_data["email"] = user.email
    create_data["roles"] = [superset_role.pk for superset_role in superset_roles]
    create_data["password"] = "admin@123"
    create_data["conf_password"] = "admin@123"
    response = session.post(SUPERSET_CREATE_USERS_URL, data=create_data)
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Create user failed'))
        return False
    self.stdout.write(self.style.SUCCESS('Create user successful'))

    # update Password for user
    if not update_superset_user_password(self, user):
        self.stdout.write(self.style.ERROR('Update password failed'))
        return False
    return True


def login_superset(self, session):
    response = session.post(SUPERSET_LOGIN_URL, data={"username": "admin", "password": "admin"})
    if response.status_code != HTTP_OK:
        self.stdout.write(self.style.ERROR('Login failed'))
        return False
    self.stdout.write(self.style.SUCCESS('Login successful'))
    return True


def execute_raw_query(query, is_result_expected):
    is_successful = True
    record = None
    connection = None
    try:
        connection = psycopg2.connect(user="bos",
                                      password="bos",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="superset")

        cursor = connection.cursor()
        cursor.execute(query)
        if is_result_expected:
            record = cursor.fetchall()
            print("You are connected to - ", record, "\n")
        else:
            connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        is_successful = False
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection is not None:
            connection.close()
        return is_successful, record


class SupersetUser:

    def __init__(self, pk, active, email, first_name, last_name, username, roles):
        self.pk = pk
        self.active = active
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.roles = roles

    @classmethod
    def from_json(cls, json):
        return cls(**json)

    def __repr__(self):
        return str(self.pk)


class SupersetRole:
    def __init__(self, pk, name, permissions):
        self.pk = pk
        self.name = name
        self.permissions = permissions

    @classmethod
    def from_json(cls, json):
        return cls(**json)

    def __repr__(self):
        return str(self.name)


class SupersetTable:
    def __init__(self, pk, database_name, link, changed_by_, modified):
        self.pk = pk
        self.database_name = database_name
        self.link = link
        self.changed_by_ = changed_by_
        self.modified = modified

    @classmethod
    def from_json(cls, json):
        return cls(**json)

    def __repr__(self):
        return str(self.database_name)


class SupersetDatabase:
    def __init__(self, pk, database_name, creator, allow_csv_upload, allow_dml, allow_run_async, backend,
                 expose_in_sqllab, modified):
        self.pk = pk
        self.database_name = database_name
        self.creator = creator
        self.allow_csv_upload = allow_csv_upload
        self.allow_dml = allow_dml
        self.allow_run_async = allow_run_async
        self.backend = backend
        self.expose_in_sqllab = expose_in_sqllab
        self.modified = modified

    @classmethod
    def from_json(cls, json):
        return cls(**json)

    def __repr__(self):
        return str(self.database_name)


class SupersetPermissionView:
    def __init__(self, pk, name):
        self.pk = pk
        self.name = name

    @classmethod
    def from_tuple(cls, tuple_data):
        return cls(pk=tuple_data[0], name=tuple_data[1])

    def __repr__(self):
        return str(self.name)
