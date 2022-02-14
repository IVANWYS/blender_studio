"""API views for storage-related things."""
import uuid

from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from common.upload_paths import get_upload_to_hashed_path
from common.storage import get_s3_post_url_and_fields


class GetUploadURLView(APIView):
    """Get an upload URL: can be used to upload large files directly to Studio's storage.

    Example usage:

    ```python
    import requests    # To install: pip install requests

    base_url = 'https://studio.blender.org/api'

    # Get an upload URL first
    response = responses.post(f'{base_url}/storage/get-upload-url/')
    upload_fields = response.json['fields']
    upload_url = response.json['url']

    # Upload your file using the upload_url
    with open(path_to_file, 'rb') as f:
        files = {'file': (os.path.basename(path_to_file), f)}
        response = requests.post(upload_url, data=upload_fields, files=files)
    # If upload is successful, HTTP response.status_code 204 is returned
    response.raise_for_status()

    # Now, use upload_path to create/update a static asset
    response = responses.post(
        f'{base_url}/static-asset/',
        data={
            'source': upload_fields['key'],
        },
    )
    ```
    """

    def post(self, request):  # noqa: D102
        path = get_upload_to_hashed_path(None, str(uuid.uuid4()))
        return Response(get_s3_post_url_and_fields(path))


class StorageViewSet(ViewSet):
    """Get an upload URL: can be used to upload large files directly to Studio's storage.

    Example usage:

    ```python
    import requests    # To install: pip install requests

    base_url = 'https://studio.blender.org/api'

    # Get an upload URL first
    response = responses.post(f'{base_url}/storage/get-upload-url/')
    upload_fields = response.json['fields']
    upload_url = response.json['url']

    # Upload your file using the upload_url
    with open(path_to_file, 'rb') as f:
        files = {'file': (os.path.basename(path_to_file), f)}
        response = requests.post(upload_url, data=upload_fields, files=files)
    # If upload is successful, HTTP response.status_code 204 is returned
    response.raise_for_status()

    # Now, use upload_path to create/update a static asset
    response = responses.post(
        f'{base_url}/static-asset/',
        data={
            'source': upload_fields['key'],
        },
    )
    ```
    """

    def create(self, request, format=None):  # noqa: D102
        path = get_upload_to_hashed_path(None, str(uuid.uuid4()))
        return Response(get_s3_post_url_and_fields(path))
