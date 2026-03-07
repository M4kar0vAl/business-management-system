# Система управления бизнесом

## Установка и запуск

### Установка

1. Клонировать репозиторий
    ```shell
    git clone https://github.com/M4kar0vAl/business-management-system.git
    ```

2. В корне проекта создать файл `.env` и наполнить по аналогии с `.env.example`

### Запуск

#### Make

```shell
make run
```

#### Docker compose

```shell
docker compose up -d --build
```

### Остановка

#### Make

```shell
make down
```

#### Docker compose

```shell
docker compose down
```

## Документация

После [установки и запуска](#установка-и-запуск) проекта документация API будет доступна по
адресу [http://localhost/docs](http://localhost/docs) 
