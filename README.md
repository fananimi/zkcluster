# ZKCluster

zkcluster is a simple app to manage zksoftware fingerprint device.

# Dependencies
* [django >= 1.7](http://djangoproject.com/ "Django Project")
* [pyzk >= 0.3](https://github.com/fananimi/pyzk/ "pyzk")

# Installation

* Add ``zkcluster`` to your INSTALLED_APPS in django's ``settings.py``:
```
INSTALLED_APPS = [
    # other apps
    'zkcluster',
]
```

* set connection timeout
```
ZK_CLUSTER = {
    'TERMINAL_TIMEOUT': 5 # default timeout
}
```

* migrate your database

```
python manage.py migrate
```

* add urls

```
urlpatterns = [
    # other urls
    url(r'^zkcluster/', include('zkcluster.urls', namespace='zkcluster')),
]
```

* run server

```
python manage.py runserver
```

* open web page url http://localhost:8000/zkcluster/
