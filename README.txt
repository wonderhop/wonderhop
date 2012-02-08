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
    
-   runserver to start developing
    
        (env)$ python manage.py runserver
    

Now you're developing!


Deploying
=========

We use fabric for deployments; it should have been installed above via pip.

fabfile.py defines a few "roles": dev, staging, and production.

-   Deploy to dev:

        (env)$ fab -R dev deploy

-   Initializing a brand-new Linode Ubuntu Server instance
    (Or, initialize a role using `-R` instead of `-H`.)

        (env)$ fab -H new-server-hostname init_all
