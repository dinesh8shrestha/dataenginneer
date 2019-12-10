# Docker

## Install

Воспользуйтесь [Official Docker install](https://docs.docker.com/install/linux/docker-ce/ubuntu/), либо же [плейбуком Ansible](more-ansible) для установки из нашего репозитория:

```bash
(ansenv) $ cd more-ansible
(ansenv) $ ansible-playbook -i hosts  site.yml`
```

## Дополнительная конфигурация

Внимание! в Облаке Mail.ru ттребуется дополнительная настройка размера пакета в сети докера:

Откройте (создайте) файл `/etc/docker/daemon.json` и занесите туда:

```
{

  "mtu": 1400

}
```

## Verify

Запустите тестовый контейнер Hello World:

```
$ sudo docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
1b930d010525: Pull complete
Digest: sha256:6540fc08ee6e6b7b63468dc3317e3303aae178cb8a45ed3123180328bcc1d20f
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
```

## Tips

Добавьте вашего теокущего юзера в группу `docker` чтобы не использовать судо для запуска команд докера:

`sudo usermod -aG docker your-user`

Нужно разлогиниться и залогиниться, чтобы это стало работать.

