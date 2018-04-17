from collections import Counter
from freq import Freq
from itertools import _grouper
from os.path import isfile
from pandas import DataFrame
import csv

from marge.cleaner import has, has_over, is_truthy, simple_has
from marge.enumerations import incompletes, nulls
from marge.utils import is_admin, is_complete, max_by_group

def run(i, save_path=None, in_memory=False, debug=False):

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
            keys = list(i[0].keys())
        elif isinstance(i, DataFrame):
            iterator = list([series.to_dict() for index, series in i.iterrows()])
            keys = list(iterator[0].keys())
        elif isinstance(i, str) and isfile(i):
            sep = "\t" if i.endswith("\t") else ","
            f = open(i)
            iterator = csv.DictReader(f, delimiter=sep)
            keys = list(iterator.fieldnames)
        elif isinstance(i, _grouper):
            for thing in _grouper:
                print("thing:", thing)
            iterator = list(_grouper)
            keys = list(iterator[0].keys())
        elif input_type == "<class 'django.db.models.query.QuerySet'>":
            iterator = i
            keys = list(iterator[0].keys())
        else:
            print("can't enrich type:", type(i))

        if debug: print("\titerator:", iterator)

        calc_country_code_frequency = "probability" in keys

        new_keys = [
            "has_enwiki_title",
            "pop_is_zero",
            "pop_at_least_1_million"
        ]

        if calc_country_code_frequency:
            new_keys.append("country_code_frequency")

        fieldnames = list(set(keys + new_keys))

        if debug: print("\tfieldnames:", fieldnames)

        if save_path:
            with open(save_path, "w") as f:
                writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
                writer.writerow()

        if in_memory:
            items = []

        if "probability" in keys and "feature_id" in keys:
            maxes = max_by_group(iterator, "probability", "feature_id")
            for item in iterator:
                fid = item["feature_id"]
                prob = item["probability"]
                item["likely_correct"] = 1 if prob == maxes[fid] else 0

        print('iterator:', type(iterator))

        if calc_country_code_frequency:
            all_country_codes = [ i["country_code"].lower() for i in iterator if i["likely_correct"] and i["country_code"] ]
            freqs = Freq(all_country_codes)
            for item in iterator:
                cc = item["country_code"].lower() if item["country_code"] else None
                item["country_code_frequency"] = freqs[cc]

        print("calced cc freqs")

        for item in iterator:
            item["percent_fields_complete"] = Freq([is_complete(v) for v in item.values()])[True]
        print("calced percent fields complete")
        s = set()
        #tracker = "has_enwiki_title"
        tracker = None
        for item in iterator:
            item["has_enwiki_title"] = simple_has(item, 'enwiki_title')
            if tracker: s.add(item[tracker])
            try:
                item["pop_is_zero"] = 1 if item["population"] in [False, None, True, 0, "false", "null", "true", "None", "True", "False"] else 0
                item["has_population_over_1_million"] = has_over(item, "population", 1e6)
                #item["has_population_over_1_thousand"] = has_over(item, "population", 1e3)
                #item["has_population_over_1_hundred"] = has_over(item, "population", 1e2)
            except Exception as e:
                print("[georich] exception adding population columns")

            try:
                item["is_admin"] = is_admin(item)
            except Exception as e:
                print("[georich] exception adding is_admin column:", e)

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

        if in_memory:
            return items
    except Exception as e:
        print("Caught exception enriching:", e)
