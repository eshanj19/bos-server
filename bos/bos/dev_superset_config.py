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

# ---------------------------------------------------------
# Superset specific config
# ---------------------------------------------------------
ROW_LIMIT = 5000

SUPERSET_WEBSERVER_PORT = 8088
# ---------------------------------------------------------

# ---------------------------------------------------------
# Flask App Builder configuration
# ---------------------------------------------------------
# Your App secret key
SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
# SQLALCHEMY_DATABASE_URI = 'sqlite:////path/to/superset.db'

SQLALCHEMY_DATABASE_URI = 'postgresql://bos:bos@localhost/superset'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = False
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []
# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''

HTTP_HEADERS = {'Access-Control-Allow-Origin': "http://192.168.0.122:3000",
                'Access-Control-Allow-Credentials': 'true'}
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    # 'allow_headers': [
    #     'X-CSRFToken', 'Content-Type', 'Origin', 'X-Requested-With', 'Accept',
    # ],
    'resources': [
        '/superset/csrf_token/',  # auth
        '/api/v1/formData/',  # sliceId => formData
        '/superset/explore_json/*',  # legacy query API, formData => queryData
        '/api/v1/query/',  # new query API, queryContext => queryData
        '/superset/fetch_datasource_metadata/'  # datasource metadata

    ],
    'origins': ['192.168.0.122:3000', '192.168.0.122:8000'],
}
