import random
import string
import os.path
import re
import json
import urllib2
import base64
from getpass import getpass
from StringIO import StringIO
from fabric.api import env, sudo, run, put, local, get
from fabric.contrib.files import exists, upload_template, contains, append
from fabric.contrib.project import rsync_project
from fabric.context_managers import cd, settings, hide
from fabric.contrib.console import confirm
from fabric.operations import require, prompt
from fabric.utils import warn, abort

def _dep(name): return os.path.join("dependencies", name)

env.user = "wonderhop"
env.key_filename = os.path.expanduser("~/.ssh/id_dsa")
env.landing = True
env.debug = True

def dev():
    env.hosts = ["dev.wonderhop.com"]
    env.landing = True
    env.debug = True

def production():
    env.hosts = ["live.wonderhop.com"]
    env.landing = True
    env.debug = True

env.repo_root = "/home/wonderhop/wonderhop"
env.proj_root = "/home/wonderhop/wonderhop/wonderhop"
env.django_wsgi_root = "/home/wonderhop/wsgi"
env.django_static_root = "/home/wonderhop/django-static"

def clone_repo():
    """Clone the wonderhop repo on the server"""
    # Add known hosts for Github
    append("~/.ssh/known_hosts", [
        "|1|AxYrTZcwBIPIFSdy29CGanv85ZE=|D0Xa0QCz1anXJ9JrH4eJI3EORH8= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==",
        "|1|ErT4pRs4faesbyNw+WB0hWuIycs=|9+4iN3FDijMOl1Z+2PNB9O9wXjw= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==",
    ])
    
    if not exists("~/.ssh/id_github_deploy"):
        # Generate a public/private key pair
        run("ssh-keygen -q -t rsa -f ~/.ssh/id_github_deploy -N ''")
        
        ssh_pub_key = StringIO()
        get("~/.ssh/id_github_deploy.pub", ssh_pub_key)
        ssh_pub_key = ssh_pub_key.getvalue().strip()
        
        # Add it to Github
        gh_user = prompt("Github username?")
        gh_pass = getpass("Github password? ")
        urllib2.urlopen(urllib2.Request("https://api.github.com/repos/wonderhop/wonderhop/keys", json.dumps({
            "title": "wonderhop@{0}".format(env.host),
            "key": ssh_pub_key,
        }), {
            "Content-Type": "application/json",
            "Authorization": "Basic {0}".format(base64.b64encode("{0}:{1}".format(gh_user, gh_pass))),
        }))
        
        # Specify that we should use the given key for Github
        append("~/.ssh/config", "Host github.com\nIdentityFile ~/.ssh/id_github_deploy")
    
    run("git clone git@github.com:wonderhop/wonderhop.git")

def copy_config_files():
    """Copies the configuration files (requires cloned repo)"""
    run("mkdir -p {0} --mode=755".format(env.django_static_root))
    run("mkdir -p {0} --mode=755".format(env.django_wsgi_root))

    deps = {
        "local_settings.py.template": (env.proj_root + "/local_settings.py", 0644, False),
        "apache.conf": ("/etc/apache2/sites-available/wonderhop", 0644, True),
        "django.wsgi": (env.django_wsgi_root + "/wonderhop.wsgi", 0644, False),
    }
    for src, (dst, mode, use_sudo) in deps.iteritems():
        upload_template(_dep(src), dst, env, use_sudo=use_sudo)
        sudo("chmod {0:o} {1}".format(mode, dst))
        sudo("rm -rf {0}.bak".format(dst))

    sudo("a2ensite wonderhop")

def update():
    """Pull the git repo and reload apache"""
    with cd(env.proj_root):
        run("git pull")
        run("./manage.py syncdb --noinput")
        run("./manage.py migrate --noinput")
        run("./manage.py collectstatic --noinput")
    service("apache2", "reload")

def manage(command):
    """Issue a command to manage.py"""
    with cd(env.proj_root):
        run("./manage.py {0}".format(command))

def init_all():
    """Call all the init tasks, then set up the site. Use on a fresh Ubuntu instance."""
    init_user()
    init_python()
    init_redis()
    init_postgres()
    init_apache()
    init_postfix()
    init_git()
    clone_repo()
    copy_config_files()
    update()

def init_user():
    """Creates a user named wonderhop for access. Copies pubkey."""
    with settings(user="root"):
        if not exists("/home/wonderhop"):
            run("useradd -m -s /bin/bash -U wonderhop")
            append("/etc/sudoers", "wonderhop ALL = NOPASSWD: ALL")
    copy_sshkey()

def init_python():
    """Install python, psycopg2, pip, and pip requirements file"""
    install_packages("python-psycopg2 python-pip python-setuptools "
                     "build-essential python-dev")

    put(_dep("requirements.txt"), "requirements.txt")
    sudo("pip install --requirement=requirements.txt")
    run("rm requirements.txt")

def init_redis():
    """Install Redis, enable service"""
    install_packages("redis-server")
    enable_service("redis-server")

def init_postgres():
    """Install postgres, create database with default permissions"""
    install_packages("postgresql-9.1")

    append("/etc/postgresql/9.1/main/pg_hba.conf", "local wonderhop wonderhop peer", use_sudo=True)

    enable_service("postgresql")
    service("postgresql", "restart") # In case it was running previously

    create_db()

def init_apache():
    """Install apache and mod_wsgi, start server"""
    install_packages("apache2 libapache2-mod-wsgi")
    enable_service("apache2")

    sudo("a2enmod wsgi")
    sudo("a2dissite default")
    service("apache2", "restart")

def init_postfix():
    """Install postfix, make it forward to Mark Lurie"""
    install_packages("postfix")
    enable_service("postfix")
    
    append("/etc/postfix/virtual", "@wonderhop.com marklurie@gmail.com", use_sudo=True)
    sudo("postmap /etc/postfix/virtual")
    append("/etc/postfix/main.cf", "virtual_alias_maps = hash:/etc/postfix/virtual", use_sudo=True)
    service("postfix", "reload")

def init_git():
    """Install git"""
    install_packages("git")

def install_packages(package_names):
    """Install packages by name (space separated)"""
    sudo("DEBIAN_FRONTEND=noninteractive apt-get install -q -y {0}".format(package_names))

def enable_service(service_name):
    """Enable a system service using update-rc.d"""
    sudo("update-rc.d {0} defaults".format(service_name))
    service(service_name, "start")

def service(service_name, cmd):
    """Pass a command to 'service'"""
    sudo("service {0} {1}".format(service_name, cmd))

def copy_sshkey():
    """Copy your public key to ~wonderhop/.ssh/authorized_keys, via root ssh"""
    with settings(user="root"):
        pubkey_filename = "{0}.pub".format(env.key_filename)
        if not os.path.exists(pubkey_filename):
            err = "Could not locate pubkey, expected at {0}"
            abort(err.format(pubkey_filename))

        key = open(pubkey_filename, "r").read().strip()
        sshdir = "~wonderhop/.ssh"
        run("mkdir -p {0}".format(sshdir))
        append("{0}/authorized_keys".format(sshdir), key)
        run("chown -R wonderhop:wonderhop {0}".format(sshdir))
        run("chmod -R o-rwx {0}".format(sshdir))

def create_db():
    """Create skeletal postgres database"""
    if env.user != "wonderhop":
        abort("create_db requires you to run as wonderhop")

    with settings(warn_only=True):
        createuser = sudo("su postgres -c 'createuser -S -D -R wonderhop'")
    if createuser.failed:
        warn("Creating database user failed. Assuming db exists.")
        return

    sudo("su postgres -c 'createdb -O wonderhop wonderhop'")
