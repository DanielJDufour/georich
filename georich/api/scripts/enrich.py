from collections import Counter
from freq import Freq
from itertools import _grouper
from os.path import isfile
from pandas import DataFrame
from re import match
from word2number import w2n
import csv

from marge.cleaner import has, has_over, is_truthy, simple_has
from marge.enumerations import incompletes, nulls
from marge.utils import is_admin, is_complete, max_by_group

def is_between(n, lowest, highest):
    if n == "":
        return 0
    else:
        try:
            return 1 if intify(lowest) <= intify(n) <= intify(highest) else 0
        except Exception as e:
            print("[is_between] returned 0 because", e)
            return 0

def intify(inpt):
    #print("starting intify with:", [inpt])
    if isinstance(inpt, int):
        return inpt
    else:
        try:
            return w2n.word_to_num(inpt.replace("_", " "))
        except:
            return int(inpt.replace("_", ""))

def run(i, new_fields=None, save_path=None, in_memory=False, debug=False, track=None):

    try:

        if debug:
            print("starting enricher")
            print("\ti:", i)
            print("\tsave_path:", save_path)
            print("\tin_memory:", in_memory)
            print("\tdebug:", debug)


        input_type = str(type(i))

        # convert input to list of dicts
        if isinstance(i, list) and isinstance(i[0], dict):
            iterator = i
            old_fields = list(i[0].keys())
        elif isinstance(i, DataFrame):
            iterator = list([series.to_dict() for index, series in i.iterrows()])
            old_fields = list(iterator[0].keys())
        elif isinstance(i, str) and isfile(i):
            sep = "\t" if i.endswith("\t") else ","
            f = open(i)
            iterator = csv.DictReader(f, delimiter=sep)
            old_fields = list(iterator.fieldnames)
        elif isinstance(i, _grouper):
            for thing in _grouper:
                print("thing:", thing)
            iterator = list(_grouper)
            old_fields = list(iterator[0].keys())
        elif input_type == "<class 'django.db.models.query.QuerySet'>":
            iterator = i
            old_fields = list(iterator[0].keys())
        else:
            print("can't enrich type:", type(i))

        if debug: print("\titerator:", iterator)

        fieldnames = list(set(old_fields + new_fields))

        if debug: print("\tfieldnames:", fieldnames)

        if save_path:
            with open(save_path, "w") as f:
                writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
                writer.writerow()

        if in_memory:
            items = []

        #print('iterator:', type(iterator))

        if "likely_correct" in iterator[0]:
            country_codes = [ i["country_code"].lower() for i in iterator if i["likely_correct"] and i["country_code"] ]
        else:
            country_codes = None

        """
        if "country_code_frequency" in new_fields:
            all_country_codes = [ i["country_code"].lower() for i in iterator if i["likely_correct"] and i["country_code"] ]
            freqs = Freq(all_country_codes)
            for item in iterator:
                cc = item["country_code"].lower() if item["country_code"] else None
                item["country_code_frequency"] = freqs[cc]

        if "place_type_frequency" in new_fields:
            all_place_types = [ i["place_type"].lower() for i in iterator if i["likely_correct"] and i["place_type"] ]
            freqs = Freq(all_place_types)
            for item in iterator:
                cc = item["place_type"].lower() if item["place_type"] else None
                item["place_type_frequency"] = freqs[cc]
        """

        #print("calc'd country code frequencies")

        possible_has_fields = ["has_" + field for field in old_fields if not field.startswith("has")]
        #print("possible_has_fields:", possible_has_fields)
        possible_is_zero_fields = [field + "_is_zero" for field in old_fields if not field.endswith("is_zero")]
        #print("possible_is_zero_fields:", possible_is_zero_fields)

        if track: tracked = set()
        for item in iterator:
            try:

                if track:
                    tracked.add(item[track])
                #print("new_fields:", new_fields)
                for field in new_fields:
                    try:
                        # check if item has a field
                        if "likely_correct" in iterator[0]:
                            item["country_code_has_match"] = 1 if (0 <= len(country_codes) <= 1) or country_codes.count(item["country_code"]) > 1 else 0


                        if field in possible_has_fields:
                            #print("field " + field + " in possible_has_fields")
                            item[field] = simple_has(item, field.replace("has_",""))
                        elif field in possible_is_zero_fields:
                            #print(field, "is zero field")
                            item[field] = 1 if item[field.replace("_is_zero","")] in ['0', 0, None, False, "null", "Null", "None"] else 0
                        else:

                            # check if item's amount is over a threshold
                            mg = match("has_(?P<original>[A-Za-z_]+)_over_(?P<n>[A-Za-z_\d]+)", field)
                            if mg:
                                #print("matched threshold")
                                item[field] = has_over(item, mg.group("original"), intify(mg.group("n")))
                                continue

                            mg = match("has_(?P<original>[A-Za-z_]+)_between_(?P<n1>[A-Za-z_\d]+)_and_(?P<n2>[A-Za-z_\d]+)", field)
                            if mg:
                                #print("matched threshold")
                                item[field] = is_between(item[mg.group("original")], mg.group("n1"), mg.group("n2"))

                    except Exception as e:
                        print("[georich] exception on field:", field, ":", e)

            except Exception as e:
                print("[georich] exception adding population columns")


            """
                Set importance is 0.25 if no importance is set.
                We're doing this because we have to to assign some value.
            """
            if "importance" in item:
                value = item["importance"]
                if value in ["", None]: item["importance"] = 0.25
                else: item["importance"] = float(item["importance"])


            # booleanify
            for key in ["correct","likely_correct"]:
                if key in item:
                    item[key] = is_truthy(item[key])

            if save_path:
                writer.writerow(item)

            if in_memory:
                if debug: print("appended:", item)
                items.append(item)

        if track:
            print("tracked:", tracked)

        if in_memory:
            return items
    except Exception as e:
        print("Caught exception enriching:", e)
