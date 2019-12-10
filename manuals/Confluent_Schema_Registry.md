# Confluent Schema Registry

```
curl -O http://packages.confluent.io/archive/5.2/confluent-5.2.2-2.12.tar.gz
gunzip confluent-5.2.2-2.12.tar.gz 
tar xvf confluent-5.2.2-2.12.tar 
cd confluent-5.2.2/
cp etc/schema-registry/schema-registry.properties etc/schema-registry/schema-registry.properties.orig
vi etc/schema-registry/schema-registry.properties 
```

Делаем исправления в конфиг файле:

Порт на котором слушает Schema Registry:

`listeners=http://0.0.0.0:8086`

Закоментируем использование zookeeper (но вы можете поэкспериментировать):

`#kafkastore.connection.url=localhost:2181`

Раскоментируем прямое обращение к кафка-брокеру по внутреннему адресу: 

`kafkastore.bootstrap.servers=PLAINTEXT://10.132.0.2:6667`

Запускаем:

`bin/schema-registry-start etc/schema-registry/schema-registry.properties`

## REST API

Check interface:

```
curl -X GET "http://localhost:8086"
{}
```

Схемы (topic-value)

```
curl -X GET http://localhost:8086/subjects/
["name_surname-value"]
```

Версии

```
curl -X GET http://localhost:8086/subjects/name_surname-value/versions
[1,2,3]
```

```
curl -X GET http://localhost:8086/subjects/name_surname-value/versions/1
{"subject":"name_surname-value","version":1,"id":1,"schema":"{\"type\":\"record\",\"name\":\"gender_age_value\",\"namespace\":\"test\",\"doc\":\"Gender age dataset\",\"fields\":[{\"name\":\"uid\",\"type\":\"string\"},{\"name\":\"gender_age\",\"type\":\"string\"},{\"name\":\"timestamp\",\"type\":\"long\"},{\"name\":\"url\",\"type\":\"string\"}]}"}
```


## Confluent python package

Напишем программу для отправки сообщений в формате avro c регистрацией схемы.
Воспользуемся пакетом c клиентом Kafka на питоне, который поддерживает использование Confluent Schema Registry.

Установите пакет в вашу виртуальную среду:

`pip install "confluent-kafka[avro]"`

Пример отправки сообщения из файла
```
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

source_file1 = base_dir + "/data/lab04_train_exploded5_s.json"

# Schema of the messages, to use with avro
schema1_str = """
{
 "doc": "Gender age dataset",
 "name":"gender_age_value",
 "namespace":"test",
 "type":"record",
 "fields": [
    {"name":"uid", "type":"string"},
    {"name":"gender_age", "type":"string"},
    {"name":"timestamp_s", "type": "long"},
    {"name":"url", "type":"string"}
 ]
}
"""

    #
    # Send message to topic_in
    #
    schema = avro.loads(schema1_str)
    producer = AvroProducer({
      'bootstrap.servers': bootstrap,
      'schema.registry.url': schema_registry_url
      }, default_value_schema=schema
    )

    with open(source_file1) as source:
      for line in source:
        if not line.startswith("{"):
          continue
        line_json = json.loads(line)
        print(line_json)
        producer.produce(topic=topic_in, value=line_json)

    producer.flush()
```

## Утилиты командной строки.

В пакете confluent, который вы укстановили, идут и утилиты для работы в консоли. Ищите их в bin.

Пример использования:

```
$ ./bin/kafka-avro-console-producer \
         --broker-list localhost:6667 --topic test \
         --property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"f1","type":"string"}]}'
```

Другие примеры - в [документации Confluent](https://docs.confluent.io/3.0.0/quickstart.html#confluent-platform-quickstart)

## Ссылки

[Confluent docs: Using Schema Registry](https://docs.confluent.io/current/schema-registry/using.html#common-sr-usage-examples)

[Пример использования](https://aseigneurin.github.io/2018/08/02/kafka-tutorial-4-avro-and-schema-registry.html) Confluent Schema Registy REST API и пример на скала.

[Schema Compatibility in Kafka](https://blog.knoldus.com/error-registering-avro-schema-multiple-schemas-in-one-topic/)

