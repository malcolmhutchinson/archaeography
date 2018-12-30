PostgreSQL: Install and configure
=================================

Install the DBMS and create user roles and databases.

go back to: [Install an archaeography server](../../archaeography_install)

You will need password for the machine role, which will be written
into the file `archaeography/home/settings.

In shell:

    # Update the repository lists.
    sudo apt-get update

    # Install PostgreSQL and PostGIS
    sudo apt-get install postgresql postgresql-contrib postgis

    # Become the user `postgres`.
    sudo su postgres

    # Create users. The P flag prompts for passwords.
    createuser -P machine

    # Create the database, with owner `machine`.
    createdb -O machine archaeography

    # create the PostGIS extension.
    psql -d archaeography -c "CREATE EXTENSION postgis;"




You may want to create a user account for yourself, and give it the
privileges of the `machine` account. Create the user in shell, then go
to the DBMS to grant privileges.

    createuser -P malcolm
    psql -d archaeography -c "GRANT machine TO malcolm;"

Done.

Next: [Install a Django development environment](django_install)







Reference
---------

Ellingwood, Justin. _How to install and use PostgreSQL on Ubuntu 16.04_.
On [digitalocean.com](http://digitalocean.com)  
Accessed 2018-11-01 from
[https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04)




