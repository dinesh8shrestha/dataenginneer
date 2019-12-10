#### Подготовка

Установка virtualenv`sudo apt-get install virtualenv`

```
ubuntu@instance-2:~$ python3 --version
Python 3.6.8
ubuntu@instance-2:~$ virtualenv --version
15.1.0
```
Установка пакета с заголовками питона:

`sudo apt-install python3-dev`

Рабочий каталог для Airflow и внутри него virtualenv каталог Python 3.

```bash
$ cd
$ pwd
/home/ubuntu
$ mkdir airflow
$ cd airflow
$ virtualenv -p /usr/bin/python3 afenv
$ source afenv/bin/activate
(afenv) $
```

#### Установка и инициализация Airflow

```
(afenv) $ pip install apache-airflow flask-bcrypt
```


Установка переменную среды `AIRFLOW_HOME`.

```
(afenv) $ mkdir airflow_home
(afenv) $ export AIRFLOW_HOME=`pwd`/airflow_home
(afenv) $ airflow initdb
(afenv) $ airflow version
[2019-08-13 14:34:20,343] {__init__.py:51} INFO - Using executor SequentialExecutor
  ____________       _____________
 ____    |__( )_________  __/__  /________      __
____  /| |_  /__  ___/_  /_ __  /_  __ \_ | /| / /
___  ___ |  / _  /   _  __/ _  / / /_/ /_ |/ |/ /
 _/_/  |_/_/  /_/    /_/    /_/  \____/____/|__/  v1.10.4
```

конфигурационный файл `airflow.cfg` в `AIRFLOW_HOME`:

```
(afenv) $ tree airflow_home/
.
├── airflow.cfg
└── unittests.cfg
```

Запуск

```
(afenv) $ airflow webserver -p 8080
```

#### Airflow scheduler

```
$ export AIRFLOW_HOME=/home/ubuntu/airflow/airflow_home
$ source $AIRFLOW_HOME/../afevn/bin/activate
(afenv) $ airflow scheduler
```

#### Запуск при загрузке 

Прописать файлы сервисов для systemd, чтобы airflow запускался автоматически при загрузке системы. 

Определить `export AIRFLOW_HOME=/home/ubuntu/airflow/airflow_home`  в `bashrc`

#### Дополнительная кофигурация

 `airflow.cfg` :

* web_server_port = 8081 #замена дефолтного 8080
* rbac = True #для авторизации пользователей UI

* auth_backend = airflow.contrib.auth.backends.password_auth #для авторизации пользователей API

`(afenv) $ airflow resetdb`

#### Web UI Admin

```bash
(afenv) $ airflow create_user -r Admin -u admin -f First -l Last -e admin@example.com -p 'admin'
```

#### API User

```python
(afenv) $ python
Python 3.6.8 (default, Jan 14 2019, 11:02:34)
[GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from airflow import models, settings
>>> from airflow.contrib.auth.backends.password_auth import PasswordUser
>>> user = PasswordUser(models.User())
>>> user.username = 'admin'
>>> user.password = 'password'
>>> session = settings.Session()
>>> session.add(user)
>>> session.commit()
>>> session.close()
>>> exit()
```

#### Начало работы 

- [Tutorial](https://airflow.apache.org/tutorial.html)
- [Security](https://airflow.apache.org/security.html)
- [Experimental Rest API Airflow](http://airflow.apache.org/api.html)

#### Проверка API:

```
$ curl http://admin:password\!@localhost:8080/api/experimental/test
{"status":"OK"}
```

```python
url = 'http://{}:{}/{}'.format(host, airflow_port,'api/experimental/test')
auth = ('admin', 'password')
uri = requests.get(url, auth=auth)
print(uri.status_code) #200 for Ok
```
#### Запуск DAG

```bash
$ curl -X POST http://admin:password\!@localhost:8080/api/experimental/dags/example_bash_operator/dag_runs -H 'Cache-Control: no-cache' -H 'Content-Type: application/json' -d '{"conf":"{\"key\":\"value\"}"}'
{"message":"Created <DagRun example_bash_operator @ 2019-08-13 19:28:45+00:00: manual__2019-08-13T19:28:45+00:00, externally triggered: True>"}
```

```python
   url2 = 'http://{}:{}/{}/{}/{}'.format(host, airflow_port,
                                        'api/experimental/dags', dag_id, 'dag_runs')
   print("airflow_trigger_dag: "+url2)

   data = {"conf":"{\"key\":\"value\"}"}
   headers = {'Content-type': 'application/json'}
   auth = ('admin', 'password')
   uri2 = requests.post(url2, data=json.dumps(data), headers=headers, auth=auth)

   return True if uri2.status_code == 200 else False
```
