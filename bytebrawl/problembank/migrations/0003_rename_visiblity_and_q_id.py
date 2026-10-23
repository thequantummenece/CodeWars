from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problembank', '0002_testcases_test_case_no_testcases_visiblity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testcases',
            old_name='visiblity',
            new_name='visibility',
        ),
        migrations.RenameField(
            model_name='testcases',
            old_name='q_id',
            new_name='problem',
        ),
    ]
