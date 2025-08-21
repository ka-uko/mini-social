# БаняNet — мини-соцсеть на Django

Учебно-итоговый проект: лента постов, лайки, комментарии (с ответами), подписки, профили.

## Технологии
- Python 3.10+
- Django 4.x / 5.x
- SQLite
- Django Templates + Bootstrap 5
- Pillow (для ImageField)

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt  # (или pip install django pillow)

# 2. Миграции
python manage.py makemigrations
python manage.py migrate

# 3. Создать суперпользователя
python manage.py createsuperuser

# 4. Запуск
python manage.py runserver
