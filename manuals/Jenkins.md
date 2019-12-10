 докер - https://jenkins.io/doc/book/installing/)

`docker pull jenkinsci/blueocean`

Теперь, внимание! В Dockerfile определен пользователь jenkins с id=1000. Если мы не хотим запускать Jenkins на нашей системе под рутом, нам надо создать пользователя с таким же id. Если у вас в системе нет пользователя с id=1000 (проверьте командой `id 1000`), то создайте пользователя `jenkins`, добавьте его в группу `docker`:

`sudo useradd --uid 1000 --no-create-home -G docker jenkins`

Если же такой юзер имеется, добавьте его в группу docker:

`sudo usermod -G docker your_user_with_id_1000`

```
docker run \
  --name jenkins1
  -u 1000 \
  --rm \
  -d \
  -p 8070:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkinsci/blueocean
```

```
INFO: 

*************************************************************
*************************************************************
*************************************************************

Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

686bb244b8f84b2888451cfd67fe9484

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword

*************************************************************
*************************************************************
*************************************************************

```


В Web UI  "Install most usefull plugins".

## Репозиторий проекта

`flask_app.py`:
```python
#
# Simple Flask app
#
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, world!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

`requirements.txt`:
```
Flask==1.0.2
```

`Dockerfile`:
```
FROM ubuntu:18.04
MAINTAINER Artem
RUN apt-get update -y && apt-get install -y python-pip python-dev build-essential
ADD . /flask-app
WORKDIR /flask-app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["flask_app.py"]
```

## Jenkins job

Вернитесь в Jenkins и создайте новую задачу: "Please create new jobs" to get started.

Выберите название проекта и категорию "Freestyle project".

В секции `Source Code Management`: выберите Git, добавьте ваш репозиторий.

В секции `Build Triggers`: выберите "Trigger builds remotely (e.g., from scripts)". Введите название токена `NEWPROLAB` - будет использоваться для проверки чекером.

В секции `Build`: выберите "execute shell", введите:

`cd docker-build; docker build -t my-flask-image:latest` (или другое название образа)

## Запуск сборки проекта

В терминале наберите команду:

`curl -X GET http://newprolab:newprojenkins@localhost:8070/job/lab-flask/build?token=NEWPROLAB`

Для отслеживания статуса зайдите на сайт: http://localhost:8070/me/my-views/view/all/

Обратите внимание, что первый запуск будет достаточно длительным, так как docker будет скачивать базовый образ.

Если сборка завершилась успешно, то детали можно посмотреть по ссылке:

http://localhost:8070/me/my-views/view/all/job/lab-flask/lastSuccessfulBuild/

в том числе, лог команды сборки в меню "Console output":

http://localhost:8070/me/my-views/view/all/job/lab-flask/lastSuccessfulBuild/console

Так же точно можно посмотреть и неуспешные сборки.

В случае успешной сборки у вас должен появиться новый образ докера, проверьте командой `docker images`.

## Запуск образа проекта

`docker run --rm -p 5000:5000 my-flask-image`

и откройте страничку по адресу `localhost:5000`

