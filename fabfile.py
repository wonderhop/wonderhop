import random
import string
import os.path
import StringIO
import re
from itertools import ifilterfalse as _ifilterfalse
from fabric.api import env, sudo, run, put, local, get
from fabric.contrib.files import exists, upload_template, contains, append
from fabric.contrib.project import rsync_project
from fabric.context_managers import cd, settings, hide
from fabric.contrib.console import confirm
from fabric.operations import require
from fabric.utils import warn, abort

def _dep(name): return os.path.join("dependencies", name)

env.user = "wonderhop"
env.key_filename = os.path.expanduser("~/.ssh/id_dsa")

def dev():
    env.hosts = ["dev.wonderhop.com"]
    env.landing = True
    env.debug = True

def production():
    env.hosts = ["wonderhop.com"]
    env.landing = True
    env.debug = True

env.django_root = "/home/wonderhop"
env.proj_root = env.django_root + "/wonderhop"
env.django_static_root = "/usr/local/django-static"

def deploy():
    """Archive from source, upload to server, collect static, and reload"""
    if local("hg st", capture=True).strip() != "":
        msg = "Uncommitted changes present, and won't be pushed. Continue?"
        if not confirm(msg, default=False):
            abort("Aborted on request.")

    for d in _ifilterfalse(exists, [env.django_root, env.django_static_root]):
        sudo("mkdir -p {0} --mode=755".format(d))
        sudo("chown wonderhop:wonderhop {0}".format(d))

    if not exists(".pgpass"):
        abort("Expected .pgpass not found.")

    pgpass = StringIO.StringIO()
    get(".pgpass", pgpass)
    re_host = re.compile(r"^localhost:\*:wonderhop:wonderhop:(\w+)$")
    pwds = filter(None, map(re_host.match, pgpass.getvalue().splitlines()))
    if len(pwds) != 1:
        abort("{0} .pgpass passwords, expected 1".format(len(pwds)))
    passwd = pwds[0].group(1)

    if os.path.exists("wonderhop.tgz"):
        abort("wonderhop.tgz exists locally, remove it.")
    for path in ["wonderhop.tgz", "wonderhop", env.proj_root + "-old"]:
        if exists(path):
            abort("{0} exists remotely, remove it.".format(path))

    local("hg archive -t tgz -I wonderhop "
          "-X wonderhop/local_settings.py.dist wonderhop.tgz")

    put("wonderhop.tgz", "wonderhop.tgz")
    local("rm wonderhop.tgz")
    run("tar --strip-components=1 -zxvf wonderhop.tgz")
    run("rm wonderhop.tgz")

    run("mkdir wonderhop/apache")

    deps = {
        "local_settings.py.template": ("wonderhop/local_settings.py", 0644, False),
        "apache.conf": ("/etc/apache2/sites-available/wonderhop", 0644, True),
        "django.wsgi": ("wonderhop/apache/django.wsgi", 0644, False),
    }
    env.database_password = "" # work around Fabric issue 316
    with settings(database_password=passwd):
        for src, (dst, mode, use_sudo) in deps.iteritems():
            upload_template(_dep(src), dst, env, use_sudo=use_sudo)
            sudo("chmod {0:o} {1}".format(mode, dst))
            sudo("rm -rf {0}.bak".format(dst))

    if exists(env.proj_root):
        run("mv {0} {0}-old".format(env.proj_root))
    run("mv wonderhop {0}".format(env.proj_root))
    run("rm -rf {0}-old".format(env.proj_root))

    with cd(env.proj_root):
        run("./manage.py collectstatic --noinput")

    sudo("a2ensite wonderhop")
    service("apache2", "reload")

def syncdb():
    """Run Django syncdb remotely"""
    with cd(env.proj_root):
        run("./manage.py syncdb --noinput")

def init_all():
    """Call all the init tasks. Use on a fresh Ubuntu instance."""
    init_user()
    init_python()
    init_redis()
    init_postgres()
    init_apache()

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

    enable_service("postgresql-9.1")
    service("postgresql-9.1", "restart") # In case it was running previously

    create_db()

def init_apache():
    """Install apache and mod_wsgi, start server"""
    install_packages("apache2 libapache2-mod-wsgi")
    enable_service("apache2")

    sudo("a2enmod wsgi") # Enable wsgi module
    service("apache2", "restart")

def install_packages(package_names):
    """Install packages by name (space separated)"""
    sudo("apt-get install -y {0}".format(package_names))

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
        run("chmod 755 {0}".format(sshdir))
        append("{0}/authorized_keys".format(sshdir), key, use_sudo=True)
        run("chmod 644 {0}/authorized_keys".format(sshdir))

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
