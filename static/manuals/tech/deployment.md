Deploying the archaeograpy server
================================

This document describes the process used to deploy an archaeography
server using Apache with mod-wsgi on a Debian OS.

Introduction
------------

We install the Django code in `/opt/archaeography/`.

It is important to set permissions to allow the code to be modified,
and to exclude the webserver user (`www-data`), so we set up a group
of users who are permitted to make changes, called `web`. I add myself
to that group. 

The tradition with Apache on Debian systems is to have files
accessible to the webserver kept in `/var/www/`. This is where the
Django static files should be collected.

The process is:

1.  Set up filespace, clone the code, and install a virtual
    environment. 

1.  Install and configure the Apache webserver.

1.  Create a deploy branch, and make changes to the settings.

1.  Get an SSL certificate, from Lets Encrypt.




Set up filespaces, and clone the code
-------------------------------------

In shell:

    cd /opt
    sudo mkdir archaeography webnote
    
    sudo chown root:web /opt/archaeography
    sudo chmod 775 /opt/archaeography

    sudo chown root:web /opt/webnote
    sudo chmod 775 /opt/webnote

    # Clone webnote from GitHub.
    git clone https://github.com/malcolmhutchinson/webnote.git /opt/webnote
    
    # Clone the archaeography code from github
    cd /opt/archaeography
    git clone git@github.com:malcolmhutchinson/archaeography.git code

    # Create a virtual environment.
    virtualenv env

    # Install the python modules
    cd /opt/archaeography/
    pip install \
        Pillow bs4 django ephem exifread markdown2 \
        mechanize psycopg2-binary requests smartypants

    # Place a symlink to webnote.
    ln -s /opt/webnote /opt/archaeography



Install and configure Apache
----------------------------

We require passwords with this application, and so it is responsible
to serve everything on an encrypted channel. We will need to create
two config files; one to redirect all traffic to the SSL file, and
then the SSL file, which will do all the work. We create and edit the
files, and then enable them with the utility `a2ensite`.

In shell:

    sudo apt-get update
    sudo apt-get install python-pip apache2 libapache2-mod-wsgi

    cd /etc/apache2/sites-available

    # Create the first config file.
    sudo nano archaeography.conf

Paste this into that file:

    <VirtualHost *:80>

        ServerName archaeography
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/

        RewriteEngine On
        RewriteCond %{HTTPS} off
        RewriteRule (.*) https://%{SERVER_NAME}$1 [R,L] 

        ErrorLog ${APACHE_LOG_DIR}/error_arch_v1.log
        CustomLog ${APACHE_LOG_DIR}/access_arch_v1.log combined

    </VirtualHost>

Create the SSL config file.

    sudo nano /etc/apache2/sites-available/archaeography-ssl.conf

Paste in this stuff:

    <IfModule mod_ssl.c>
        <VirtualHost archaeography.ruapehu:443>

            ServerAdmin webmaster@localhost
            ServerName archaeography.ruapehu:443
            DocumentRoot /var/www/archaeography

            ErrorLog ${APACHE_LOG_DIR}/error_archaeography.log
            CustomLog ${APACHE_LOG_DIR}/access_archaeography.log combined

            SSLEngine On

            SSLCertificateFile /etc/ssl/certs/selfsigned.crt
            SSLCertificateKeyFile /etc/ssl/certs/private.key

            <Directory /opt/archaeography-v1.0/code/home>
                <Files wsgi.py>
                    Require all granted
                </Files>
            </Directory>

            Alias /static/ /var/www/archaeography/

            BrowserMatch "MSIE [2-6]" \
                nokeepalive ssl-unclean-shutdown \
                downgrade-1.0 force-response-1.0
            # MSIE 7 and newer should be able to use keepalive
            BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown

        </VirtualHost>

    </IfModule>

    WSGIScriptAlias / /opt/archaeography-v1.0/code/home/wsgi.py
    WSGIPythonHome /opt/archaeography-v1.0/env
    WSGIPythonPath /opt/archaeography-v1.0/code/


Enable the configuration:

    sudo a2ensite archaeography-v1.0.conf
    sudo a2ensite archaeography-v1.0-ssl.conf

Create a self-signed SSL certificate

    cd /etc/ssl/certs
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 /
        -keyout /etc/ssl/certs/private.key -out /etc/ssl/certs/selfsigned.crt

Make sure the rewrite and ssl modules are installed:

    sudo a2enmod rewrite
    sudo a2enmod ssl

Test the configuration files with

    apachectl configtest

Which will give you syntax errors.

Restart the server

    sudo /etc/init.d/apache2 restart

The server will probably run, but if you visit it, you might get a
bunch of errors, because we haven't changed the settings yet.




Change the settings for deployment
----------------------------------

First, once the Django code has been cloned from github, make a new
branch to keep the changes we must make for deployment. In shell:

    cd /opt/archaeography/code
    git checkout -b deploy

In the `home.setting.py` file:


    DEBUG = True

    # Prevent transmission over non-encrypted protocol. 
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    # People to be sent email on 500-level errors
    ADMINS = [
        ('Full name', 'email address'),
    ]

Also, change the SECRET_KEY variable to some other long string of
random characters.







Static files
------------

Next step, link the file libraries to the static files collection. 

    cd /opt/archaeography/code/static
    ln -s /srv/geolib geolib
    ln -s /srv/nzaa nzaa


Now, here's where we do things in a bit of a tricky way. To avoid
problems with version control, it is better to keep all the static
files under the `/opt/archaeography/code/static` directory. But apache
will be looking for files to serve under `/var/www/archaeography/`. So
we make a symlink from there to here.

    ln -s /opt/archaeography/code/static /var/www/archaeography


some static
files, like the CSS scripts and these manuals, are under version
control with the codebase,

