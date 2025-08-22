from django.db import migrations


def seed_tags(apps, schema_editor):
    ServiceTag = apps.get_model('accounts', 'ServiceTag')
    data = [
        ("parmaster", "Пармастер"),
        ("massage", "Массаж, оздоровительные процедуры"),
        ("rent", "Предоставляю баню в аренду"),
    ]
    for code, title in data:
        ServiceTag.objects.get_or_create(code=code, defaults={"title": title})


def unseed_tags(apps, schema_editor):
    ServiceTag = apps.get_model('accounts', 'ServiceTag')
    ServiceTag.objects.filter(code__in=["parmaster", "massage", "rent"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_servicetag_user_avatar_user_bio_user_city_user_role_and_more'),
        # ↑ если у тебя номер другой — поставь актуальный id предыдущей миграции
    ]

    operations = [
        migrations.RunPython(seed_tags, reverse_code=unseed_tags),
    ]
