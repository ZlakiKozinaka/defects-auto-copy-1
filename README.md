## Описание

Система для учета дефектов автомобилей.
Проект развернут с использованием Docker Compose и включает:
- web: Django-приложение
- db: PostgreSQL
- данные PostgreSQL хранятся на серверном диске в /database
- бэкапы базы сохраняются в /backup

## Первый запуск

1. Перейти в папку проекта
```bash
cd /opt/defects-auto
```

2. Поднять контейнеры
```bash
docker compose up -d --build
```

3. Применить миграции
```bash
docker compose exec web python manage.py migrate
```

4. Заполнить справочники
```bash
docker compose exec web python manage.py seed_initial_data
```

5. Создать суперпользователя
```bash
docker compose exec web python manage.py createsuperuser
```

После этого сайт доступен по адресу:
http://defects-auto.irito.ru/

## Обновление проекта

1. Сделать backup базы
```bash
docker compose exec -T db pg_dump -U postgres defects_auto | gzip > /backup/backup_$(date +\%Y-\%m-\%d_\%H-\%M).sql.gz
```

2. Обновить файлы проекта

3. Перезапустить контейнеры
```bash
docker compose up -d --build
```

4. Применить миграции
```bash
docker compose exec web python manage.py migrate
```

5. При необходимости повторно выполнить
```bash
docker compose exec web python manage.py seed_initial_data
```

## Автоматический backup базы
### Проверка вручную
```bash
docker compose exec -T db pg_dump -U postgres defects_auto | gzip > /backup/test_backup.sql.gz
ls /backup
```

### Настройка cron
Открыть планировщик:
```bash
crontab -e
```

Добавить строки:
```bash
15 12 * * * cd /opt/defects-auto && docker compose exec -T db pg_dump -U postgres defects_auto | gzip > /backup/backup_$(date +\%Y-\%m-\%d_\%H-\%M).sql.gz
15 17 * * * cd /opt/defects-auto && docker compose exec -T db pg_dump -U postgres defects_auto | gzip > /backup/backup_$(date +\%Y-\%m-\%d_\%H-\%M).sql.gz
0 3 * * * find /backup -type f -mtime +7 -delete
```

### Проверка cron
```bash
crontab -l
```

### Восстановление базы
```bash
gunzip -c backup.sql.gz | docker compose exec -T db psql -U postgres defects_auto
```

## !!!Важно!!!
Не выполнять:
```bash
docker compose down -v
```

Эта команда удалит данные базы данных. Допустимо использовать:
```bash
docker compose down
```
