from django.db import migrations

def seed_provider_backfill(apps, schema_editor):
    ServiceTag = apps.get_model('accounts', 'ServiceTag')
    data = [
        ('steam_master', 'Пармастер'),
        ('rent_bath',    'Предоставляю баню в аренду'),
        ('massage',      'Массаж, оздоровительные процедуры'),
    ]
    for code, title in data:
        ServiceTag.objects.get_or_create(code=code, defaults={'title': title})

def unseed_provider_backfill(apps, schema_editor):
    # Обычно бэкфилл не откатывают, но дадим безопасный откат только «наших» кодов
    ServiceTag = apps.get_model('accounts', 'ServiceTag')
    ServiceTag.objects.filter(code__in=['steam_master', 'rent_bath']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_seed_more_servicetags'),  # или последняя у тебя в accounts
    ]

    operations = [
        migrations.RunPython(seed_provider_backfill, reverse_code=unseed_provider_backfill),
    ]
