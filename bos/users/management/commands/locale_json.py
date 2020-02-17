import json
import re

from django.core.management.base import BaseCommand


def get_po_path(locale, domain, locale_dir):
    return locale_dir + "/" + locale + "/LC_MESSAGES/" + domain + ".po"


# noinspection SpellCheckingInspection
def extract_from_po_file(po_path):
    with open(po_path, 'r', encoding='utf-8') as f:
        tuples = re.findall(r"msgid \"(.+)\"\nmsgstr \"(.+)\"", f.read())

    return tuples


def po_to_json(locales, domain, locale_dir):
    # create PO-like json data for i18n
    for locale in locales:
        obj = {}
        ra = {}
        obj['ra'] = ra

        locale_file_path = 'static/locale_' + locale + '.json'
        tuples = extract_from_po_file(get_po_path(locale, domain, locale_dir))
        for tuple in tuples:
            key = tuple[0]
            translation = tuple[1]
            if "." in key:
                print(key)
                list = key.split(".")
                arr = list[1]
                keyname = list[2]
                dict = ra.get(arr, None)
                if dict:
                    ra[arr][keyname] = translation
                else:
                    ra[arr] = {}
                    ra[arr][keyname] = translation
            else:
                ra[key] = translation
            # obj[locale][tuple[0]] = tuple[1]
        print(obj)
        with open(locale_file_path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)
    return


class Command(BaseCommand):
    help = 'Create locale json files in static dir'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        locales = ["hi_IN", "en_IN"]
        domain = "django"
        localeDir = "locale"
        po_to_json(locales, domain, localeDir)
        return
