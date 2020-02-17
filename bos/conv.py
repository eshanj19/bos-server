from datetime import timedelta, timezone, datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.utils.translation import gettext as _
from django.utils import translation
from django.utils.translation import activate, get_language_info


_("ra.action.save"),

_("ra.action.create"),

_("ra.action.edit"),

_("ra.action.delete"),

_("ra.action.add_filter"),

_("ra.action.add"),

_("ra.action.back"),

_("ra.action.bulk_actions"),

_("ra.action.bulk_cancel"),

_("ra.action.clear_input_value"),

_("ra.action.export"),

_("ra.action.list"),

_("ra.action.remove_filter"),

_("ra.action.remove"),

_("ra.action.search"),

_("ra.action.show"),

_("ra.boolean.true"),

_("ra.boolean.false"),

_("ra.action.refresh"),

_("ra.validation.required"),

_("ra.validation.minLength"),

_("ra.validation.maxLength"),

_("ra.validation.minValue"),

_("ra.validation.maxValue"),

_("ra.validation.number"),

_("ra.validation.email"),

_("ra.validation.oneOf"),

_("ra.validation.regex"),

_("ra.title.first_name"),

_("ra.title.middle_name"),

_("ra.title.last_name"),

_("ra.title.current_password"),

_("ra.title.password"),

_("ra.title.gender"),

_("ra.title.full_name"),

_("ra.title.email"),

_("ra.action.active"),

_("ra.title.created_on"),

_("ra.title.last_mod"),

_("ra.title.username"),

_("ra.title.confirm_password"),

_("ra.title.permission_group"),

_("ra.title.name"),

_('ra.title.users'),

_("ra.title.resources"),

_("ra.option.curriculum"),

_("ra.option.training_session"),

_("ra.option.file"),

_("ra.option.registration_form"),

_("ra.title.description"),

_("ra.title.day"),

_("ra.title.type"),

_("ra.title.label"),

_("ra.title.uom"),

_("ra.title.inputtype"),

_("ra.title.measurement"),

_("ra.title.athlete"),

_("ra.title.value"),

_("ra.action.submit"),

_("ra.title.name_of_ngo"),

_("ra.title.first_name_ngo_admin"),

_("ra.title.last_name_ngo_admin"),

_("ra.title.username_ngo_admin"),

_("ra.title.emailaddress_ngo_admin"),

_("ra.menu.reading"),

_("ra.menu.measurement_type"),

_("ra.menu.ngo"),

_("ra.title.set_parent"),

_("ra.title.names_of_permission_group"),

_("ra.title.is_active"),

_("ra.title.view_edit_organisation")








