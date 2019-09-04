# Tasks App

This is a simple tasks applications.
This django  project requires Python 3.6, Django version 2.2.5 and SQLite3 database.


Build instructions
==================

1) Create virtualenv. It is a good practice to keep your projects in separated environments: virtualenv lib is recommended.

2) Install::
        pip install -r task_app\requirements.txt

3) You don't need to create and migrate database. Database with all sample data is in db.sqlite3 file.

4) Run::
        python manage.py runserver





TDD
====

TDD is a good practice to avoid functional complexity  and focus on what you need to achieve.
Rus unit tests of the project:

Just run::
        python manage.py test tasks --settings=task_app.settings_tests



Project structure
====================
-> task_app (contains all files of the project despite of templates)
--> task_app (contains configuration files of the project: settings.py, settings_test.py, urls.py and wsgi.py)
--> tasks (app with main ``business logic``, ``unit tests`` and ``data migrations``)
--> templates (folder with .html files, ordered by applications)



