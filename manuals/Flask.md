# Flask

Flask - это фреймворк для web-приложений на питон

## Установка 

Создайте виртуальный или конда энвайронмент flaskenv, и установите туда пакет Flask c зависимостями.

## Приложение

Вот код для приложения типа "Hello World":

```
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

создайте файл flask-app.py с этим кодом.

## Запуск и тестирование

Запустите:

```
(flaskenv) ubuntu@cluster1-4-16-40gb:~/flask$ python ./flask-app.py 
 * Serving Flask app "flask-app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 235-907-475
```

Зайдите браузером на страничку http://localhost:5000 (или http://ваш_ip:5000 - в зависимости от того, открыт ли ваш файрвол или каким методом прокси вы пользуетесь).

У вас должна появиться надпись `Hello, World!`

Теперь откройте новый терминал и вызовите там curl с вашим URL:

```
(flaskenv) ubuntu@cluster1-4-16-40gb:~$ curl http://localhost:5000
Hello, world!(flaskenv) ubuntu@cluster1-4-16-40gb:~$ 
```

Посмотрите в терминал, где запущен ваш сервер:

```
127.0.0.1 - - [14/Oct/2019 09:50:17] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [14/Oct/2019 09:50:17] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [14/Oct/2019 09:51:10] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [14/Oct/2019 09:52:06] "GET / HTTP/1.1" 200 -
```

это ваши запросы в логе.

### REST API

Хотя вы можете и приукрасить вашу страничку с помощью HTML, нам наиболее интересно использование сервера через REST API.

Сделайте еще один endpoint, например:

```
from flask import request

@app.route('/do_something/<int:my_param>', methods=['POST'])
def do_something(my_param):
    return(f"PARAMETER {my_param}\nPOST DATA: {request.json}\n")
```

и сделайте вызов следующим образом:

```
(flaskenv) ubuntu@cluster1-4-16-40gb:~$ curl -X POST -H "Content-Type: application/json" -d '{"test-key":"test-value"}' http://localhost:5000/do_something/3
PARAMETER 3
POST DATA: {'test-key': 'test-value'}
```

Метод GET используется по умолчанию, то есть как в `hello_world()`, параметры выдираются из строки URL следующим образом:

```
@app.route('/do_comething_with_params', methods=['GET'])
def do_something_with_params():
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')
```

Вот еще пример для обработки ошибок и вывода json одновременно:

```
from flask import request, abort, make_response, jsonify

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found. Bad luck!'}), 404)
```
