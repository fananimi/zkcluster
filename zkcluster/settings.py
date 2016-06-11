from django.conf import settings

def get_config():
    '''
    Returns ZKCluster's configuration in dictionary format. e.g:
    ZK_CLUSTER = {
        'TERMINAL_TIMEOUT': 5
    }
    '''
    return getattr(settings, 'ZK_CLUSTER', {})

def get_terminal_timeout():
    return get_config().get('TERMINAL_TIMEOUT', 5)
