#ДАРИЕДУ
==============
Backend telegram web app для НКО "Дари еду"
==============

-----------
Установка и запуск через докер
-----------
### Windows и Linux:
Установить и запустить докер https://www.docker.com/  
После этого в терминале клонируете репозиторий и создаете сеть:
``` bash
git clone https://github.com/dariedu/darieduBackend.git
cd darieduBackend
docker network create mynetwork
```
При последующих запусках для обновления файлов:  
``` bash 
git pull
```  
В папку darieduBackend кладете файл .env (закеплен в канале разработчиков), потом в терминале из директории darieduBackend запускаете докер: 
``` bash
docker-compose up 
```
Первый запуск может занять пару минут. В приложении Docker должен появиться контейнер dariedubackend, в нем должно выполняться (running) два процесса: db и dariedu-server.  
Возможно, вместо ```docker-compose``` сработает ```docker compose```.  
Выход: Ctrl+C    
  
При последующих запусках для обновления файлов:  
``` bash 
git pull
```  
И далее перезапуск докера:
``` bash
docker-compose up --build
```


Для создания админа (суперпользователя), при запущенном докере в соседнем терминале из директории darieduBackend:
``` bash
docker-compose exec -ti dariedu-server python manage.py createsuperuser
```
Вводите tg-id (сейчас валидации нет, любое число > 0), пароль дважды (при введении пароль не отображается), если говорит, что пароль слишком простой/короткий, пишете Y, готово.  

----------
Сервер с API запустится по адресу http://127.0.0.1:8000/api  
swagger: http://127.0.0.1:8000/api/swagger  
админ-панель: http://127.0.0.1:8000/admin здесь нужно ввести данные админа (суперпользователя).


Для просмотра логов:
``` bash
docker logs dariedubackend-dariedu-server-1
```