# from pipe import split_in_columns
#
#
# def test_split_in_columns_default_message():
#     # one line string but a nice way in Python to wrap over multiple lines
#     expected = ('Hello world!|We hope that you are learning a lot of Python.|'
#                 'Have fun with our Bites of Py.|Keep calm and code in Python!'
#                 '|Become a PyBites ninja!')
#
#     actual = split_in_columns()
#     assert actual == expected
#
#
# def test_split_in_columns_on_other_message():
#     expected = 'Hello world:|I am coding in Python :)|How awesome!'
#
#     message = 'Hello world:\nI am coding in Python :)\nHow awesome!'
#     actual = split_in_columns(message)
#
#     assert actual == expected
