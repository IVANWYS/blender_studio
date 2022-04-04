# Generated by Django 3.2.9 on 2022-04-04 14:14

import common.validators
from django.db import migrations, models


known_template_variables = {
    # Frontpage
    ('frontpage_header', 'Work in progress rendering of Einar.'),
    ('frontpage_secondary_cta_text', 'Read the announcement'),
    ('frontpage_secondary_cta_link', '/blog/announcing-project-heist-high-end-cinematic-experience/'),

    # /welcome/ page
    ('welcome_button_text', ''),
    ('welcome_button_url', ''),
    ('welcome_header', ''),
    ('welcome_primary_text', """


Blender Studio is the creative part of the Blender HQ. A dedicated team of artists and developers who challenge themselves with creative-technical targets to help Blender users and to drive Blender development forward. This happens in an open source production environment and by sharing everything they make in an open and free license.


Want to know more? Join the studio today and help the team to create & share.


"""),
    ('welcome_secondary_text', "Access to all training, assets\nand films for €9.90/month"),
    ('welcome_title', "The Creators Who Share"),
}


def add_template_variables(apps, schema_editor):
    TemplateVariable = apps.get_model('common', 'TemplateVariable')
    TemplateVariable.objects.bulk_create(
        TemplateVariable(key=key, text=text) for key, text in known_template_variables
    )


def remove_remplate_variables(apps, schema_editor):
    TemplateVariable = apps.get_model('common', 'TemplateVariable')
    TemplateVariable.objects.filter(key__in=known_template_variables).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(help_text='Name of the variable, use this to access the variable in the template context.', max_length=30, unique=True, validators=[common.validators.validate_variable_key])),
                ('text', models.TextField(blank=True, default='', help_text='Text value of the variable. Use "{{ key.text }}" to refer to this value in a template.', max_length=500)),
                ('image', models.ImageField(blank=True, help_text='Image value of the variable. Use "{{ key.url }}" to access URL of this image in a template.', null=True, upload_to='')),
            ],
            options={
                'abstract': False, 'ordering': ['key'],
            },
        ),
        migrations.RunPython(add_template_variables, reverse_code=remove_remplate_variables),
    ]
