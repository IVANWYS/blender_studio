# Generated by Django 3.0.14 on 2021-11-09 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0006_rename_content_html'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='description',
            field=models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n<p title="<a>, <abbr>, <acronym>, <b>, <blockquote>, <code>, <em>, <i>, <li>, <ol>, <strong>, <ul>, <a>, <audio>, <caption>, <cite>, <col>, <colgroup>, <figcaption>, <figure>, <footer>, <img>, <p>, <source>, <table>, <tbody>, <td>, <tfoot>, <th>, <thead>, <tr>">Some HTML tags are allowed&nbsp;<img alt="Allowed HTML tags" src="/static/admin/img/icon-unknown.svg" class="help help-tooltip"></p>'),
        ),
        migrations.AlterField(
            model_name='section',
            name='text',
            field=models.TextField(blank=True, help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n<p title="<a>, <abbr>, <acronym>, <b>, <blockquote>, <code>, <em>, <i>, <li>, <ol>, <strong>, <ul>, <a>, <audio>, <caption>, <cite>, <col>, <colgroup>, <figcaption>, <figure>, <footer>, <img>, <p>, <source>, <table>, <tbody>, <td>, <tfoot>, <th>, <thead>, <tr>">Some HTML tags are allowed&nbsp;<img alt="Allowed HTML tags" src="/static/admin/img/icon-unknown.svg" class="help help-tooltip"></p>'),
        ),
        migrations.AlterField(
            model_name='training',
            name='description',
            field=models.TextField(help_text='Description consisting of a few sentences.'),
        ),
        migrations.AlterField(
            model_name='training',
            name='summary',
            field=models.TextField(help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment AttachmentID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n<p title="<a>, <abbr>, <acronym>, <b>, <blockquote>, <code>, <em>, <i>, <li>, <ol>, <strong>, <ul>, <a>, <audio>, <caption>, <cite>, <col>, <colgroup>, <figcaption>, <figure>, <footer>, <img>, <p>, <source>, <table>, <tbody>, <td>, <tfoot>, <th>, <thead>, <tr>">Some HTML tags are allowed&nbsp;<img alt="Allowed HTML tags" src="/static/admin/img/icon-unknown.svg" class="help help-tooltip"></p>'),
        ),
    ]
