VERSION = (0,1)

default_app_config = 'zkcluster.apps.ZkclusterConfig'


def get_user_model():
    from django.apps import apps as django_apps
    from django.conf import settings

    try:
        return django_apps.get_model(settings.ZK_USER_MODEL)
    except ValueError:
        raise ImproperlyConfigured("ZK_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ZK_USER_MODEL refers to model '%s' that has not been installed" % settings.ZK_USER_MODEL
        )
