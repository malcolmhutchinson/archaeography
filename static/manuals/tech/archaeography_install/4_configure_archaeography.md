Configuring the archaeography server
====================================


Create users and groups and other records, to make the server usable.

Before this: [Install Django](django_install)


Groups and users for the archaeography project

In shell:

    cd ~/dev/archaeography/code
    source ../env/bin/activate
    ./manage.py createsuperuser

Follow the prompts. Then start the development serever, and point a
browser at `localhost:8000/admin`. Using the Django admin interface,
create the following group:

    nzaa

Using the django admin interface, create as many user records as
required, adding membership to the appropriate groups.

Back to: [Installing an archaeography server](archaeography_install)

