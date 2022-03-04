# noqa: D100
from typing import Optional, Any, Dict, List
import logging

import meilisearch
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from common.types import assert_cast
from search import TRAINING_INDEX_UIDS, _wait_for_task, _assert_task_succeeded
from search.health_check import MeiliSearchServiceError, check_meilisearch

logger = logging.getLogger(__name__)


class Command(BaseCommand):  # noqa: D101
    help = (
        f'Create the main search index "{settings.MEILISEARCH_INDEX_UID}", its replica'
        f'indexes, and the training search index; or only update their settings if the'
        f'indexes already exist.'
    )

    def _get_or_create_index(self, index_uid: str) -> meilisearch.index.Index:
        try:
            task = settings.SEARCH_CLIENT.create_index(index_uid, {'primaryKey': 'search_id'})
            logger.debug(task)
            task_status, error_code = _wait_for_task(task)
            if error_code == 'index_already_exists':
                self.stdout.write(f'The index "{index_uid}" already exists. Skipping creation...')
            elif task_status != 'succeeded':
                raise Exception(
                    'Unable to create index %s: task failed with status "%s", error code: %s',
                    index_uid,
                    task_status,
                    error_code,
                )
        except Exception as err:
            raise CommandError(err)
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created the index "{index_uid}".'))
        index = settings.SEARCH_CLIENT.get_index(index_uid)
        return index

    def handle(self, *args: Any, **options: Any) -> Optional[str]:  # noqa: D102
        try:
            check_meilisearch()
        except MeiliSearchServiceError as err:
            raise CommandError(err)

        # Create or update the main index, the replica indexes, and the training index
        main_search_ranking_rules = assert_cast(dict, settings.MAIN_SEARCH['RANKING_RULES'])
        training_search_ranking_rules = assert_cast(dict, settings.TRAINING_SEARCH['RANKING_RULES'])
        indexes_and_ranking_rules: Dict[str, List[str]] = {
            **main_search_ranking_rules,
            **training_search_ranking_rules,
        }
        for index_uid, ranking_rules in indexes_and_ranking_rules.items():
            index = self._get_or_create_index(index_uid)
            _assert_task_succeeded(index.update_ranking_rules(ranking_rules))

            if index_uid in TRAINING_INDEX_UIDS:
                _assert_task_succeeded(
                    index.update_searchable_attributes(
                        settings.TRAINING_SEARCH['SEARCHABLE_ATTRIBUTES']
                    )
                )
                _assert_task_succeeded(
                    index.update_filterable_attributes(
                        settings.TRAINING_SEARCH['FACETING_ATTRIBUTES']
                    )
                )
                _assert_task_succeeded(
                    index.update_sortable_attributes(
                        settings.TRAINING_SEARCH['SORTABLE_ATTRIBUTES']
                    )
                )
            else:
                _assert_task_succeeded(
                    index.update_searchable_attributes(
                        settings.MAIN_SEARCH['SEARCHABLE_ATTRIBUTES']
                    )
                )
                _assert_task_succeeded(
                    index.update_filterable_attributes(settings.MAIN_SEARCH['FACETING_ATTRIBUTES'])
                )
                _assert_task_succeeded(
                    index.update_sortable_attributes(settings.MAIN_SEARCH['SORTABLE_ATTRIBUTES'])
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully updated the index "{index_uid}".'))

        return None
