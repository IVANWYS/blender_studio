# Generated by Django 3.0.9 on 2020-12-11 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0059_meta_entry_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='description',
            field=models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='text',
            field=models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n'),
        ),
        migrations.AlterField(
            model_name='filmflatpage',
            name='content',
            field=models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n'),
        ),
    ]
