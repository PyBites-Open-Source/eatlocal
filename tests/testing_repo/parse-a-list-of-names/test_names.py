from names import (
    NAMES,
    dedup_and_title_case_names,
    sort_by_surname_desc,
    shortest_first_name,
)

PY_CONTENT_CREATORS = [
    "brian okken",
    "michael kennedy",
    "trey hunner",
    "matt harrison",
    "julian sequeira",
    "dan bader",
    "michael kennedy",
    "brian okken",
    "dan bader",
]


def test_dedup_and_title_case_names():
    names = dedup_and_title_case_names(NAMES)
    assert names.count("Bob Belderbos") == 1
    assert names.count("julian sequeira") == 0
    assert names.count("Brad Pitt") == 1
    assert len(names) == 10
    assert all(n.title() in names for n in NAMES)


def test_dedup_and_title_case_names_different_names_list():
    actual = sorted(dedup_and_title_case_names(PY_CONTENT_CREATORS))
    expected = [
        "Brian Okken",
        "Dan Bader",
        "Julian Sequeira",
        "Matt Harrison",
        "Michael Kennedy",
        "Trey Hunner",
    ]
    assert actual == expected


def test_sort_by_surname_desc():
    names = sort_by_surname_desc(NAMES)
    assert names[0] == "Julian Sequeira"
    assert names[-1] == "Alec Baldwin"


def test_sort_by_surname_desc_different_names_list():
    names = sort_by_surname_desc(PY_CONTENT_CREATORS)
    assert names[0] == "Julian Sequeira"
    assert names[-1] == "Dan Bader"


def test_shortest_first_name():
    assert shortest_first_name(NAMES) == "Al"


def test_shortest_first_name_different_names_list():
    assert shortest_first_name(PY_CONTENT_CREATORS) == "Dan"
