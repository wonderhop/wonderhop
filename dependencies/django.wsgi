import sys, os
sys.path.append("%(repo_root)s")
os.environ["DJANGO_SETTINGS_MODULE"] = "wonderhop.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
