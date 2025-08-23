# accounts/migrations/0009_seed_all_servicetags_hardening.py
from django.db import migrations

ALL_TAGS = [
    # Банные услуги (provider)
    ("steam_master", "Пармастер"),
    ("massage", "Массаж, оздоровительные процедуры"),
    ("rent_bath", "Предоставляю баню в аренду"),
    # Строительство бань (builder)
    ("build", "Строю бани"),
    ("consult_build", "Консультирую по строительству бань"),
    # Продажа товаров (seller)
    ("brooms", "Веники"),
    ("clothes", "Одежда"),
    ("accessories", "Аксессуары/принадлежности"),
    ("cosmetics", "Банная косметика/мыло"),
]

def ensure_all_tags(apps, schema_editor):
    ServiceTag = apps.get_model("accounts", "ServiceTag")
    for code, title in ALL_TAGS:
        ServiceTag.objects.get_or_create(code=code, defaults={"title": title})

def noop(apps, schema_editor):
    # Ничего не удаляем при откате
    pass

class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_seed_provider_backfill"),
    ]

    operations = [
        migrations.RunPython(ensure_all_tags, reverse_code=noop),
    ]
