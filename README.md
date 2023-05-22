# FR_test

Fill conf.yaml:
- your token: token
- your time between checking the database for new mailings: check_base_rate

To prepare project, execute next commands:
- make build

To start project execute:
- make start

To stop project execute:
- make stop

To remove saved data and remove unused docker data:
- make clean

To restart project (build, start):
- make restart

For more info about API open swagger.yaml in root of app.


Сделал следущий дополнительные задания:

3.подготовить docker-compose для запуска всех сервисов проекта одной командой

5.сделать так, чтобы по адресу /docs/ открывалась страница со Swagger UI и в нём отображалось описание разработанного API. 

12.обеспечить подробное логирование на всех этапах обработки запросов, чтобы при эксплуатации была возможность найти в логах всю информацию по:

    •id рассылки - все логи по конкретной рассылке (и запросы на api и внешние запросы на отправку конкретных сообщений)

    •id сообщения - по конкретному сообщению (все запросы и ответы от внешнего сервиса, вся обработка конкретного сообщения)

    •id клиента - любые операции, которые связаны с конкретным клиентом (добавление/редактирование/отправка сообщения/…)
