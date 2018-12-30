Django: install and configure
=============================

Install the archaeography code in a Django development space, and the
tables in the database.

Before this: [Clone the code from GitHub](github_clone)

Run the Django migrations to set up the database. In shell:

    cd ~/dev/archaeography/code
    source ../env/bin/activate

    # Run migrations to create the basic database structures.
    ./manage.py migrate

    # Make and run migrations for applications
    ./manage.py makemigrations geolib members nzaa
    ./manage.py migrate geolib
    ./manage.py migrate members
    ./manage.py migrate nzaa

    # Create an account for yourself, with superuser prvileges:
    ./manage.py createsuperuser


You should now be able to run the development server and visit the
website with your browser.

Next: [Add users and groups](archaeography_configure)