# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cuenta_validada',
            field=models.BooleanField(default=True, verbose_name='Cuenta Validada'),
        ),
        migrations.AlterField(
            model_name='user',
            name='rol',
            field=models.CharField(
                choices=[
                    ('participante', 'Participante'),
                    ('organizador', 'Organizador'),
                    ('sponsor', 'Sponsor'),
                    ('admin', 'Administrador')
                ],
                default='participante',
                max_length=20,
                verbose_name='Rol'
            ),
        ),
    ]
