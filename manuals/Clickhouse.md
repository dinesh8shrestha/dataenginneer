##  Установка ClickHouse на одной ноде

```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4

echo "deb http://repo.yandex.ru/clickhouse/deb/stable/ main/" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update

sudo apt-get install -y clickhouse-server clickhouse-client
```

Оставьте пароль пользователя по умолчанию пустым.

## Конфигурация

Вся конфигурация сервера находится в файле `/etc/clickhouse-server/config.xml`

### Конфликт портов

Порт нативного клиента Clickhouse 9000 находится в конфликте с каким-то другим сервисом кластера. Замените его в строке файла с тэгами:

`    <tcp_port>9090</tcp_port>`

### Listen_host

По умолчанию сервер слушает на локальном интерфейсе, а не внешнем. Чтобы запускать запросы удаленно с чекера, добавьте настройку:

`<listen_host>0.0.0.0</listen_host>`

### Кластер

Кликхауз может работать в кластерном режиме, в котором некоторые запросы обрабатываются параллельно на всех узлах кластера. Создайте кластер `cluster1` из двух узлов (головного и его соседа по региону), пользуясь шаблоном из config.xml. Коротко говоря, надо вставить теги `<cluster1>...</cluster1>` внутри  `<remote_servers incl="clickhouse_remote_servers" >` и теги с шардами ` <shard>... </shard>` на каждый узел. Для лабораторной работы вам потребуется кластер из двух узлов, так что можете его определить в конфиге заранее. Никаких дополнительных ресурсов это не потребует. Оба узла кластера будут использовать один и тот же конфиг-файл, просто скопируйте его.

## Start

`sudo service clickhouse-server start`

## Clickhouse plugin for Logstash

Если вы уже установили ELK, то установите [logstash-output-clickhouse plugin](https://github.com/mikechris/logstash-output-clickhouse), который позволит вставлять данные в таблицы Clickhouse используя Logshash. Это понадобится в первой лабе.

```
$ cd /usr/share/logstash/
$ sudo bin/logstash-plugin install logstash-output-clickhouse
Validating logstash-output-clickhouse
Installing logstash-output-clickhouse
Installation successful
```

## Работа с клиентом

Обратите внимание на порт, который вы меняли в конфиге сервера.

### Create

```
cat <<END | clickhouse-client --port 9090 --multiline
CREATE TABLE example
  (
     timestamp DateTime,
     referer String,
 )
 ENGINE = MergeTree()
 PARTITION BY toYYYYMM(timestamp)
 PRIMARY KEY timestamp
 ORDER BY timestamp
 SETTINGS index_granularity = 8192
END
```

```
clickhouse-client --port 9090 --query="show tables"
```

```
clickhouse-client --port 9090 --query="show create table example"
```

### Insert

`cat lab04_train_exploded.json | clickhouse-client --port 9090 --multiline --query="INSERT into name_surname_lab01s_gender_age_dist format JSONEachRow"`

### Select

`clickhouse-client --port 9090 --query="select count(uid) from name_surname_lab01s_gender_age_dist"`

## Работа с питоновской библиотекой clickhouse-driver

Установите питоновский пакет в среду `afenv`, где у вас уже установлен Airflow:

`(afenv) $ pip3 install clickhouse-driver`

Этот пакет использует не REST API, а нативный протокол, так что смотрите внимательно какой порт вы используете для нативного клиента:

```
from clickhouse_driver import Client

client = Client(host='localhost', port=9090)

#
# Select query example
#
query = "select toUnixTimestamp(max(timestamp)) from {}".format(table_name)
res = client.execute(query)
print(res)

#
# insert query example
#  

# export pandas dataframe to json:
values = json.loads(df_flat.to_json(lines=False, orient='records'))
# print(json.dumps(values, indent=4))

query = "INSERT INTO {} VALUES".format(table_name)
res = client.execute(query, values)
```

[Документация](https://clickhouse-driver.readthedocs.io/en/latest/) по пакету очень хороша.

## Работа c REST API

По умолчанию, clickhouse_port должен быть 8123.

### Проверка API

Питон:
```python
   uri = 'http://{}:{}'.format(host, clickhouse_port)
   res = requests.get(uri)
   is_success = res.status_code == 200
```

### Запрос

Питон:
```python
    query = "DESCRIBE {}".format(table)
    uri = requests.get('http://{}:{}/?query={}'.format(host, clickhouse_port, urllib.quote(query)))
    print("clickhouse_check_table: {}".format(query))
    print(uri.text)
    #400 for malformed request, 404 for table does not exists
    return True if uri.status_code == 200 else False
```

## Ссылки

По этой [ссылке](https://www.altinity.com/blog/2017/12/18/logstash-with-clickhouse) можно прочитать, как подсоединить Logstash напрямую к ClickHouse.
