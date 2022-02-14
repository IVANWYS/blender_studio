"""API viewsets for static assets."""
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from common.storage import get_s3_post_url_and_fields
from common.upload_paths import get_upload_to_hashed_path
from static_assets.serializers import StaticAssetSerializer, UploadSerializer
import static_assets.models


class UploadViewSet(ViewSet):
    """Get an upload URL: can be used to upload large files directly to Studio's storage.

    Example usage:

    ```python
    import os.path
    import requests

    api_url = 'https://studio.blender.org/api'
    api_token = 'YOUR_API_TOKEN'
    headers = {'Authorization': f'Token {api_token}', 'Content-Type': 'application/json'}

    path_to_source_file = 'path/to/file.mp4'
    path_to_thumbnail_file = 'path/to/image.png'


    def upload_file(path_to_file):
        # Get an upload URL first
        response = requests.post(
            f'{api_url}/upload/',
            json={'original_filename': os.path.basename(path_to_file)},
            headers=headers,
        )
        response.raise_for_status()
        response_json = response.json()

        upload_fields = response_json['fields']
        upload_url = response_json['url']

        # Upload file to the upload_url
        with open(path_to_file, 'rb') as f:
            files = {'file': (os.path.basename(path_to_file), f)}
            response = requests.post(upload_url, data=upload_fields, files=files)
        # If upload is successful, HTTP response.status_code 204 is returned
        response.raise_for_status()
        print(f'Uploaded to {upload_fields["key"]}')
        return upload_fields['key']


    # Upload both source and thumbnail files
    source_upload_path = upload_file(path_to_source_file)
    thumbnail_upload_path = upload_file(path_to_thumbnail_file)

    # Now, use the resulting upload paths to create a static asset
    response = requests.post(
        f'{api_url}/static-asset/',
        json={
            'source_path': source_upload_path,
            'thumbnail_path': thumbnail_upload_path,
        },
        headers=headers,
    )
    response.raise_for_status()
    static_asset_id = response.json()['id']
    print(f'Created a static asset, ID: {static_asset_id}')
    ```
    """

    # Use StaticAsset to make this (model-less) view set use model permissions
    queryset = static_assets.models.StaticAsset.objects.none()
    serializer_class = UploadSerializer

    def get_view_name(self):
        """Override name of this viewset."""
        return 'Get upload URL'

    def create(self, request, *args, **kwargs):  # noqa: D102
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        path = get_upload_to_hashed_path(None, data['original_filename'])
        return Response(
            self.serializer_class(data={**data, **get_s3_post_url_and_fields(path)}).initial_data
        )


class StaticAssetViewSet(viewsets.ModelViewSet):
    """List, create, update or search static assets.

    To create or update static assets files,
    use [Get Upload URL](/api/upload/) to upload the files first.
    """

    queryset = static_assets.models.StaticAsset.objects.all()
    serializer_class = StaticAssetSerializer
    search_fields = [
        'source',
        'original_filename',
        'user__full_name',
        'user__email',
        'author__full_name',
        'author__email',
        'source_type',
        'section__name',
        'assets__name',
    ]
    filter_backends = (filters.SearchFilter,)

    def perform_create(self, serializer):
        """Set additional fields before saving."""
        serializer.validated_data['user'] = self.request.user
        super().perform_create(serializer)
