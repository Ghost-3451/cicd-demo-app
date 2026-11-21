# Calculator: локальный CI/CD

Приложение использует функции `src/calculator.py`. HTTP-обёртка запускается на
`0.0.0.0:8080` внутри контейнера. Снаружи контейнер доступен только по адресу
`http://127.0.0.1:18080` (порт можно изменить параметром `APP_PORT`).

## Подготовка среды

Jenkins, Docker Engine, Python и Ansible должны работать в одной Ubuntu.
Jenkins установлен как системная служба, пользователь службы — `jenkins`.
Для Docker используется сокет `unix:///var/run/docker.sock`.

Нужны Git, curl, Python 3.10+, python3-venv, Docker Engine и доступ пользователя
`jenkins` к группе `docker`. После изменения групп службу Jenkins перезапускают.
Доступ к Docker проверяется командой:

```bash
sudo -u jenkins -H env DOCKER_HOST=unix:///var/run/docker.sock docker info
