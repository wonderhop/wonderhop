Getting Started
===============

-   pip for package management
    
        $ easy_install pip
    
-   use virtualenv to isolate your packages
    
        $ pip install virtualenv
        $ virtualenv --no-site-packages env
    
-   activate your virtualenv
    (repeat this step in every console you open for wonderhop)
    
        $ source env/bin/activate
    
-   install the required packages
    
        (env)$ pip install --requirement=dependencies/requirements.txt
    
-   syncdb to set up Django models
    
        (env)$ cd wonderhop/
        (env)$ python manage.py syncdb
    
-   migrate to apply South migrations
    
        (env)$ python manage.py migrate
    
-   copy the default local settings file to get some sensible defaults
    
        (env)$ cp local_settings.py.dist local_settings.py
    
-   runserver to start developing
    
        (env)$ python manage.py runserver
    

Now you're developing!


Deploying
=========

We use fabric for deployments; it should have been installed above via pip.

fabfile.py defines two sets of server settings, dev and production.

-   Deploy to dev:

        (env)$ fab dev update

-   Deploy to production:

        (env)$ fab production update

-   Initializing a brand-new Linode Ubuntu Server instance

        (env)$ fab -H new-server-hostname init_all

After you change config files, you'll need to run the copy_config_files task.

After you install new Python packages and add them to requirements.txt,
you'll need to run the init_python task.
