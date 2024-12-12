from typing import List


NAMES = [
    "arnold schwarzenegger",
    "alec baldwin",
    "bob belderbos",
    "julian sequeira",
    "sandra bullock",
    "keanu reeves",
    "julbob pybites",
    "bob belderbos",
    "julian sequeira",
    "al pacino",
    "brad pitt",
    "matt damon",
    "brad pitt",
]


def dedup_and_title_case_names(names: list) -> List:
    """Should return a list of title cased names,
    each name appears only once"""
    titled = [name.title() for name in names]
    return list(set(titled))


def sort_by_surname_desc(names: list) -> List:
    """Returns names list sorted desc by surname"""
    names = dedup_and_title_case_names(names)
    return sorted(names, key=lambda x: x.rsplit(None, 1)[-1], reverse=True)


def shortest_first_name(names: list) -> str:
    """Returns the shortest first name (str).
    You can assume there is only one shortest name.
    """
    names = dedup_and_title_case_names(names)
    return sorted(
        [name.split(" ")[0] for name in names], key=lambda x: len(x.split()[0])
    )[0]
