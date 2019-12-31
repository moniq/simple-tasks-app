SKY django challenge
-------------------------


Requirements
=================

This django  project requires Python 3.6, Django version 2.2.5 and SQLite3 database.

Third-party libraries that are necessary to run the project: django-rest-framework version 3.10.3.

Build instructions
==================

1) Create virtualenv. (It is a good practice to keep your projects in separated environments: virtualenv library is recommended.)

2) Install::

        pip install -r task_app\requirements.txt

3) You don't need to create and migrate database. Database with all sample data is in db.sqlite3 file.

4) Run::

        python manage.py runserver

        # or with settings module:
        python manage.py runserver --settings=task_app.settings_staging


5) Visit http://localhost:8000/

Main page presents full list of tasks ordered by parents and ids.
![main page](https://github.com/moniq/simple-tasks-app/blob/master/static/img/main_page.png)

TDD
====

TDD is a good practice to avoid functional complexity  and focus on what you need to achieve.
Rus unit tests of the project:

Just run::

        python manage.py test tasks --settings=task_app.settings_tests



Project structure
====================

- main directory - contains all files and structure of the project)

- /task_app/ (contains configuration files of the project: settings_staging.py, settings_test.py, urls.py and wsgi.py)

- /tasks/ (app with main ``business logic``, ``unit tests`` and ``data migrations``)

- /templates/ (folder with .html files, ordered by applications)


REST API
===========

The project includes REST api functionality.

Endpoints:

        # list of all tasks
        http://localhost:8000/api/

        # task details
        http://localhost:8000/api/task/<:id>/
        example: http://localhost:8000/api/task/1/
