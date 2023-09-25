import logging
import os
import pathlib
import shutil
import tempfile

from bson import ObjectId

from django.contrib.auth import get_user_model

from cloud_import.management import mongo
from cloud_import.management.mixins import ImportCommand
from cloud_import.management.files import download_file_from_storage, upload_file_to_s3

logger = logging.getLogger('archive')
logger.setLevel(logging.INFO)
User = get_user_model()

# TODO: are there files linked to attract_asset?
# TODO: what about group_texture?
IGNORED_TYPES = {'comment', 'post', 'attract_asset', 'attract_task', 'group_texture', 'page'}


class Command(ImportCommand):
    help = 'Download and archive Cloud files of a given user'

    def add_arguments(self, parser):
        parser.add_argument(
            '-i', '--blender-id', dest='blender_id', type=int, help="Blender ID of the user"
        )
        parser.add_argument('-e', '--email', dest='email', type=str, help="Email of the user")

    def _collect_assets_and_files(self, node):
        node_type = node['node_type']
        name = node['name']
        logger.debug('Found node %s id=%s "%s"', node_type, node['_id'], name)
        if node_type == 'group':
            for next_node in mongo.nodes_collection.find(
                {
                    '$or': [{'project': ObjectId(node['_id'])}, {'parent': ObjectId(node['_id'])}],
                    '_deleted': {'$ne': True},
                }
            ):
                if next_node['_id'] == node['_id']:
                    continue
                self._collect_assets_and_files(next_node)
        elif node_type == 'asset':
            file_id = node['properties'].get('file')
            if not file_id:
                logger.warning('Asset document %s has no file', node)
                return
            self._add_file(file_id)
        elif node_type in {'texture', 'hdri'}:
            files = node['properties'].get('files', [])
            for _file in files:
                # TODO: why texture files don't exist most of the times?
                self._add_file(_file['file'])
        elif node_type in IGNORED_TYPES:
            pass
        else:
            import pprint

            pprint.pprint(node)
            raise Exception(f'Unknown node type {node_type}')

    def _add_file(self, file_id):
        if file_id in self.file_nodes:
            return
        file_doc = mongo.files_collection.find_one({'_id': file_id})
        if not file_doc:
            logger.warning('File %s does not exist', file_id)
            return
        self.file_nodes[file_id] = file_doc

    def handle(self, *args, **options):
        blender_id = None
        if options['email']:
            user_docs = mongo.users_collection.find({'email': options['email']})
        elif options['blender_id']:
            blender_id = options['blender_id']
            user_docs = mongo.users_collection.find(
                {'auth.provider': 'blender-id', 'auth.user_id': str(options['blender_id'])}
            )
        logger.info('Found %s users', user_docs.count())
        avatar_ids = set()
        self.file_nodes = {}
        blender_ids = set()
        for user_doc in user_docs:
            if 'avatar' in user_doc and user_doc['avatar'].get('file'):
                avatar_ids.add(user_doc['avatar']['file'])
            for auth in user_doc['auth']:
                if auth['provider'] == 'blender-id':
                    blender_ids.add(int(auth['user_id']))
            logger.debug('Found %s user', user_doc)
            projects = mongo.projects_collection.find(
                {'user': ObjectId(user_doc['_id']), '_deleted': {'$ne': True}}
            )
            logger.info('Found %s projects', projects.count())
            for project in projects:
                nodes = mongo.nodes_collection.find(
                    {
                        '$or': [
                            {'project': ObjectId(project['_id'])},
                            {'parent': ObjectId(project['_id'])},
                            {'user': ObjectId(user_doc['_id'])},
                        ],
                        '_deleted': {'$ne': True},
                    }
                )
                logger.info('Found %s nodes', nodes.count())
                for node in nodes:
                    self._collect_assets_and_files(node)

            for file_node in mongo.files_collection.find(
                {'user': ObjectId(user_doc['_id']), '_deleted': {'$ne': True}}
            ):
                self.file_nodes[file_node['_id']] = file_node
        self.file_nodes = {
            key: file_ for key, file_ in self.file_nodes.items() if file_['_id'] not in avatar_ids
        }

        if not blender_id and blender_ids:
            assert (
                len(blender_ids) <= 1
            ), f'Multiple Blender ID found for this account: {blender_ids}'
            blender_id = list(blender_ids)[0]

        if not self.file_nodes:
            logger.info('No files found')
            return

        # import pprint
        # pprint.pprint(self.file_nodes)
        logger.info('Found %s files in total', len(self.file_nodes))
        root_dir = pathlib.Path('_cloud_archives')
        base_dir = pathlib.Path(str(blender_id))
        assert (
            blender_ids and blender_id is not None and str(blender_id) in map(str, blender_ids)
        ), (
            'Blender ID is given but does not match one found in user records: '
            f'{blender_id} not in {blender_ids}'
        )
        with tempfile.TemporaryDirectory(dir=root_dir) as temp_dir:
            _dir = temp_dir / base_dir
            for key, file_ in self.file_nodes.items():
                if file_['_id'] in avatar_ids:
                    continue
                logger.info('Downloading file %s', key)
                os.makedirs(_dir, exist_ok=True)
                download_file_from_storage(file_, _dir)

            archive_base_name = f'cloud_archive_{blender_id}'
            shutil.make_archive(archive_base_name, 'zip', root_dir=temp_dir, base_dir=base_dir)

        archive_file = f'{archive_base_name}.zip'
        shutil.move(archive_file, root_dir)

        upload_file_to_s3(
            root_dir / archive_file, f'archives/{archive_file}', ContentType='application/zip'
        )
