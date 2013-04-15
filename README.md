Installation
============

Must have Python 2.7 with virtualenv installed first.

Get the package source code

    $ git clone https://github.com/vietdt/inventory-builder.git
    $ cd inventory-builder/

Create a python virtual env inside the package

    $ virtualenv .

Install dependencies

    $ ./bin/pip install -r requirements.txt

Usage
=====

Run crawler

    $ ./bin/python caab.py

Find the output file in inventory-builder/data/ folder.
