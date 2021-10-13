"""One-time helper for fixing training videos metadata on S3."""
import logging
import mimetypes

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3
import botocore
from training.models import Training

logger = logging.getLogger(__name__)
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
s3 = boto3.resource(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME


def _get_s3_object(key):
    # check if this key already exists in S3
    try:
        return s3.Object(BUCKET_NAME, key)
    except botocore.exceptions.ClientError as e:
        print(e.response)
        if e.response['Error']['Code'] != "404":
            print(e.response)
            raise


class Command(BaseCommand):
    """See below."""

    help = 'Fix Content headers on existing trainings to make them downloadable.'

    def _handle_video_source(self, source, content_type, content_disposition):
        if not source:
            # logger.error('No source file: %s, nothing to do', source)
            return
        _path = source.name
        original_mimetype, _ = mimetypes.guess_type(_path)
        assert (
            content_type == original_mimetype
        ), f'Wrong stored content type: {content_type} != {original_mimetype} of {_path}'
        _file = _get_s3_object(_path)
        if not _file:
            logger.warning('Missing file %s', _path)
            return
        old_metadata = {
            'ContentType': _file.content_type,
            'CacheControl': _file.cache_control,
        }
        metadata = {
            'ContentType': content_type,
            'CacheControl': settings.AWS_S3_OBJECT_PARAMETERS['CacheControl'],
        }
        if old_metadata['ContentType'] != metadata['ContentType']:
            self.wrong_content_type += 1
        if content_disposition and _file.content_disposition != content_disposition:
            self.wrong_disposition += 1
            metadata['ContentDisposition'] = content_disposition
            old_metadata['ContentDisposition'] = ''
        if old_metadata['CacheControl'] != metadata['CacheControl']:
            self.wrong_cache_control += 1
        if old_metadata != metadata:
            logger.warning(f'Replacing metadata: {old_metadata} -> {metadata}')
            _file.copy_from(
                CopySource={
                    'Bucket': BUCKET_NAME,
                    'Key': _file.key,
                },
                # This is the only way to update metadata, apparently
                MetadataDirective='REPLACE',
                **metadata,
            )

    def _handle_video(self, asset):
        video = asset.video
        variations = video.variations.all()
        for var in variations:
            self._handle_video_source(var.source, var.content_type, var.content_disposition)
        return

    def handle(self, *args, **options):
        """Do what is described in help."""
        self.wrong_content_type, self.wrong_disposition, self.wrong_cache_control = 0, 0, 0
        # for v in Training.objects.filter(
        #    chapters__sections__static_asset__original_filename__icontains='0-0_introduction.mp4'
        # ):
        for v in Training.objects.all():
            for c in v.chapters.all():
                for s in c.sections.all():
                    asset = s.static_asset
                    if not getattr(asset, 'video', None):
                        continue
                    self._handle_video(asset)
        if self.wrong_content_type:
            logger.warning(f'Wrong Content-Type: {self.wrong_content_type}')
        if self.wrong_disposition:
            logger.warning(f'Wrong Content-Disposition: {self.wrong_disposition}')
        if self.wrong_cache_control:
            logger.warning(f'Wrong Cache-Control: {self.wrong_cache_control}')
