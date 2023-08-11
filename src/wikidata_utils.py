import json


def load_wikidata_cache() -> dict:
    with open("../data/wikidata_cache.json", "r") as f:
        return json.load(f)


def does_wikidata_concept_aleady_exist(
    cache: dict, wikidata_id: str, wikidata_label: str
) -> bool:
    return wikidata_id in cache.values() or wikidata_label in cache


def update_wikidata_cache(wikidata_id, label) -> dict:
    cache = load_wikidata_cache()
    cache[label] = wikidata_id
    with open("../data/wikidata_cache.json", "w") as f:
        json.dump(cache, f)
    return cache


def wikidata_id_sort(item):
    # check if item is an int
    if isinstance(item, int):
        return item
    if item.startswith("Q"):
        return int(item[1:])
    return float("inf")
