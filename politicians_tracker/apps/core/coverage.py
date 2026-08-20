# Coverage configuration file
[run]
source = politicians_tracker.apps.core
branch = True
omit =
    */migrations/*
    */tests/*
    */__pycache__/*
    manage.py
    */wsgi.py
    */asgi.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:

[html]
directory = htmlcov
