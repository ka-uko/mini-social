from django.db import migrations

def seed_more_tags(apps, schema_editor):
    ServiceTag = apps.get_model('accounts', 'ServiceTag')
    data = [
        # Строительство бань (builder)
        ('build',         'Строю бани'),
        ('consult_build', 'Консультирую по строительству бань'),
        # Продажа товаров (seller)
        ('brooms',     'Веники'),
        ('clothes',    'Одежда'),
        ('accessories','Аксессуары/принадлежности'),
        ('cosmetics',  'Банная косметика/мыло'),
    ]
    for code, title in data:
        ServiceTag.objects.get_or_create(code=code, defaults={'title': title})

def unseed_more_tags(apps, schema_editor):
    ServiceTag = apps.get_model('accounts', 'ServiceTag')
    codes = ['build','consult_build','brooms','clothes','accessories','cosmetics']
    ServiceTag.objects.filter(code__in=codes).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_servicetag_options_alter_user_options_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_more_tags, reverse_code=unseed_more_tags),
    ]
