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

from enum import Enum

from measurements.models import Measurement


class DefaultMeasurementType(Enum):
    STUDENT_BASELINE = "Student Baseline"
    STUDENT_PROGRESSION = "Student Progression"
    COACH_BASELINE = "Coach Baseline"
    COACH_PROGRESSION = "Coach Progression"
    NGO_BASELINE = "NGO Baseline"
    NGO_PROGRESSION = "NGO Progression"


DEFAULT_MEASUREMENT_TYPES = [DefaultMeasurementType.STUDENT_BASELINE.value,
                             DefaultMeasurementType.STUDENT_PROGRESSION.value,
                             DefaultMeasurementType.COACH_BASELINE.value,
                             DefaultMeasurementType.COACH_PROGRESSION.value,
                             DefaultMeasurementType.NGO_BASELINE.value,
                             DefaultMeasurementType.NGO_PROGRESSION.value]

DEFAULT_NGO = "Bridges of Sports"
DEFAULT_NGO_ADMIN_EMAIL = "admin@bridgesofsports.org"
DEFAULT_NGO_ADMIN_USERNAME = "bos_admin"
DEFAULT_NGO_ADMIN_FIRST_NAME = "BOS"

DEFAULT_NGO_ADMIN_LAST_NAME = "Admin"

DEFAULT_STUDENT_BASELINES = [('Has student migrated?', Measurement.TEXT, ''),
                             ('Participated at division/zonal level last year?', Measurement.TEXT, ''),
                             ('Participated at taluka level last year?', Measurement.TEXT, ''),
                             ('Participated at district level last year?', Measurement.TEXT, ''),
                             ('Participated at state level last year?', Measurement.TEXT, ''),
                             ('Participated at national level last year?', Measurement.TEXT, ''),
                             ('Participated at international level last year?', Measurement.TEXT, ''),
                             ('Region', Measurement.TEXT, ''),
                             ('Father\'s occupation', Measurement.TEXT, ''),
                             ('Mother\'s occupation', Measurement.TEXT, ''),
                             ('Annual income of family', Measurement.TEXT, ''),
                             ('Number of Siblings', Measurement.TEXT, ''),
                             ('Eldest sibling education', Measurement.TEXT, ''),
                             # ('Events (100, 200 etc)', Measurement.TEXT, ''),
                             ('Years spent in place of birth', Measurement.TEXT, '')
                             ]

DEFAULT_COACH_BASELINES = [('Region', Measurement.TEXT, ''),
                           ('Annual Salary', Measurement.TEXT, ''),
                           ('Income from sports', Measurement.TEXT, ''),
                           ('Martial Status (optional)', Measurement.TEXT, ''),
                           ('Number of kids (optional)', Measurement.TEXT, ''),
                           ('Number of boys trained last year', Measurement.TEXT, ''),
                           ('Number of girls trained last year', Measurement.TEXT, ''),
                           ('Average number of training hour provided last year', Measurement.TEXT, ''),
                           ]

DEFAULT_STUDENT_PROGRESSIONS = [('100m dash time', Measurement.TEXT, ''),
                                ('Leg raises', Measurement.TEXT, ''),
                                ('BMI', Measurement.TEXT, ''),
                                ('Pushups (1 min)', Measurement.TEXT, ''),
                                ('Situps (1 min)', Measurement.TEXT, ''),
                                ('Left leg squats (1 min)', Measurement.TEXT, ''),
                                ('Right leg squats (1 min)', Measurement.TEXT, ''),
                                ('Overhead throw (mt)', Measurement.TEXT, 'mt'),
                                ('Broad Jump (mt)', Measurement.TEXT, 'mt'),
                                ('Vertical Jump (mt)', Measurement.TEXT, 'mt'),
                                ('Agility test', Measurement.TEXT, 'seconds'),
                                ('Crunches (1 min)', Measurement.TEXT, ''),
                                ('Beep test (levels)', Measurement.TEXT, ''), ]

DEFAULT_PERMISSIONS_BLACKLIST = [
    "add_logentry",
    "change_logentry",
    "delete_logentry",
    "view_logentry",
    "add_permission",
    "change_permission",
    "delete_permission",
    "view_permission",
    "add_contenttype",
    "change_contenttype",
    "delete_contenttype",
    "view_contenttype",
    "add_session",
    "change_session",
    "delete_session",
    "view_session",
    "add_mobileauthtoken",
    "change_mobileauthtoken",
    "delete_mobileauthtoken",
    "view_mobileauthtoken",
    "add_userresetpassword",
    "change_userresetpassword",
    "delete_userresetpassword",
    "view_userresetpassword",
]
