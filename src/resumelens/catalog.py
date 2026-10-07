"""Load the catalog distributed as a package resource."""
import json
from importlib.resources import files


def load_catalog():
    return json.loads(files("resumelens").joinpath("skills_catalog.json").read_text(encoding="utf-8"))


def validate_catalog(catalog):
    seen = {}
    canonicals = set()
    for skill in catalog["skills"]:
        canonical = skill["canonical"]
        if canonical in canonicals or not skill["category"] or not skill["aliases"]:
            raise ValueError("Duplicate symbol, empty category or symbol without aliases")
        canonicals.add(canonical)
        for alias in skill["aliases"]:
            if not alias or alias != alias.strip():
                raise ValueError("Empty alias or surrounding whitespace")
            key = alias.casefold()
            if key in seen:
                raise ValueError("Duplicate or conflicting alias: " + alias)
            seen[key] = canonical
    if not {a.casefold() for a in catalog["ambiguous_aliases"]} <= seen.keys():
        raise ValueError("Undefined ambiguous alias")
