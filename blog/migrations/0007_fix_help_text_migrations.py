# Generated by Django 3.0.14 on 2021-11-10 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_modify_help_texts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(help_text='\n<p>Format the content in <a href="https://commonmark.org/help/">Markdown</a>.</p>\n<div>\n    <p>\n        To make images float left or right of the text, use the following:\n    </p>\n    <p>\n        <code>\n        {attachment StaticAssetID class=\'float-left\'}\n        </code>\n    </p>\n    <p>\n        <code>\n        {attachment StaticAssetID class=\'float-right\'}\n        </code>\n    </p>\n</div>\n<p title="<a>, <abbr>, <acronym>, <b>, <blockquote>, <code>, <em>, <i>, <li>, <ol>, <strong>, <ul>, <a>, <audio>, <caption>, <cite>, <col>, <colgroup>, <figcaption>, <figure>, <footer>, <img>, <p>, <source>, <table>, <tbody>, <td>, <tfoot>, <th>, <thead>, <tr>">Some HTML tags are allowed&nbsp;<span class="help help-tooltip">ℹ</span>'),
        ),
    ]
