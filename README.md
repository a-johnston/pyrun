## pyrun

Some mostly junk code that executes an idea I had a few days ago. Pretty much I
was looking at some method which we wanted to run some of the time from CLI and
some of the time from other code. As the method was added to and updated, the
docstring and argparse fell out of sync with one another. I thought it might be
cool to be able to generate and parse valid options from the method signature
and docstring.

This code is pretty gross and I really don't recommend using it for anything
serious because there's a bunch of spooky behavior that is definitely a feature
not a bug because it tries its best even with inconsistent / mixed / missing
information. For example, type information can be pulled from type annotations
which could be used for validation (if I ever add that, anyways) but the type
reST value for the parameter would be used for the help string. Or even more
spooky, named positional arguments can passed in any order, and even mixed in
with varargs (see example).

Example: (using the dummy function in `example/dummy.py`)
```
user@host> ./pyrun.py example.dummy product -h
Usage:
    product --a --b [args]... [name=value]...

    a (int)   : first required positional argument
    b (float) : second required positional argument

Literally just calculates a product lol

user@host> ./pyrun.py example.dummy product 1 --a 2 --b 3 4 test=1 key=2
48
```
