# Клиент-серверный голосовой чат на основе сокетов

> Приложение писалось в качестве домашнего задания из курса "Сервис-ориентированные архитектуры" ПМИ ВШЭ.

## Постановка задачи

**Цель:** на языке высокого уровня (Java, C#, Python и др. – на выбор обучающегося) реализовать сетевое клиент-серверное приложение – голосовой чат (в виде консольного либо диалогового приложения) на основе технологии сокетов. Клиентская программа предоставляет пользователю интерфейс ввода имени пользователя и подключения к серверу, обеспечивает отправку аудио-сигнала серверу и получает от сервера аудио-сигнал от остальных пользователей.

**Задача:**
1. Реализовать базовое клиент-серверное приложение «Hello World» на основе сокетов.
2. Реализовать клиентское и серверное приложение для голосового чата с самим собой (echo). <br>
   - *Клиент обеспечивает:*
      -  Установку имени пользователя;
      -  Подключение к серверу по сетевому имени/адресу;
      -  Отправку голосовых сообщений;
      -  Получение и воспроизведение сообщений от сервера;
      -  Отключение от сервера. <br>
   - *Сервер обеспечивает:*
      -  Подключение одного пользователя;
      -  Получение сообщений от пользователя и отправку их обратно;
      -  Отключение пользователя от сервера.
3. Модифицировать клиент и сервер таким образом, чтобы они обеспечивали:
   - Общение 2-х и более пользователей одновременно;
   - Отправку сообщений от пользователей только в случае наличия сигнала либо только при нажатой кнопке (push-to-talk) – на усмотрение разработчика.
   - Вывод списка подключенных пользователей, идентификацию говорящего пользователя;
   - Актуализацию списка пользователей при подключении и отключении.
4. Модифицировать клиент и сервер таким образом, чтобы они обеспечивали возможность работы с «Комнатами». Подключение пользователей должно происходить в комнату с уникальным идентификатором (в дальнейшем, идентификаторы позволят связать комнаты с сеансами игры). Каждый пользователь может быть подключен только к одной комнате, и слышать сообщения только от тех пользователей, что подключены к этой комнате.

## Запуск приложения

### Локально

Прежде всего необходимо установить зависимости:
```
pip install -r requirements.txt
```

#### Сервер
> Необходимо наличие `python` версии `>3.7`

Запуск приложения:
```
python3 vchat/server/server.py PORT
```
где `PORT` - порт, на котором вы хотите запустить сервер. Если не указывать этот параметр при запуске, сервер будет работать на 8888 порту.

#### Клиент
> Необходимо наличие `python` версии `>3.7`

Запуск приложения:
```
python3 vchat/client/client.py IP PORT
```
где `IP` - ip-адрес, на котором запущен сервер. Если не указывать этот параметр при запуске, клиент будет обращаться к 127.0.1.1

где `PORT` - порт, на котором запущен сервер. Если не указывать этот параметр при запуске, клиент будет обращаться к 8888 порту.

### Docker
> Необходимо наличие докера

#### Сервер
```
docker pull zhukowladimir/sockets-voice-chat
docker run -it -d --name YOUR-CONTAINER-NAME zhukowladimir/serialization_test
```
Если вы хотите пробросить порт, то следует добавить флаг `-p EX-PORT:PORT`.

## Работа с приложением

### Клиент

Напишите в консоль `mute`, чтобы замьютиться.

Напишите в консоль `unmute`, чтобы размьютиться.

Нажмите `Ctrl+C` или напишите `exit`, чтобы выйти из чата.


