from typing import Tuple, Optional, Dict, List
import logging
import time

from django.conf import settings

from common.types import assert_cast

logger = logging.getLogger(__name__)
default_app_config = 'search.apps.SearchConfig'
DEFAULT_TASK_TIMEOUT = 60  # seconds


MAIN_INDEX_UIDS: List[str] = list(assert_cast(dict, settings.MAIN_SEARCH['RANKING_RULES']).keys())
TRAINING_INDEX_UIDS: List[str] = list(
    assert_cast(dict, settings.TRAINING_SEARCH['RANKING_RULES']).keys()
)
ALL_INDEX_UIDS = [*MAIN_INDEX_UIDS, *TRAINING_INDEX_UIDS]


def _wait_for_task(
    task: Dict[str, str], timeout: int = DEFAULT_TASK_TIMEOUT
) -> Tuple[Optional[str], Optional[str]]:
    total_wait_time = 0
    attempts = 0
    logger.debug('Waiting for task %s', task)
    task_uid = task['uid']
    while True:
        task = settings.SEARCH_CLIENT.get_task(task_uid)
        status = task['status']
        if status in {'succeeded', 'failed'}:
            logger.debug(task)
            return status, task.get('error', {}).get('code', '')
        if total_wait_time >= timeout:
            logger.error(
                'Task %s took too long to finish (%s), giving up', task_uid, total_wait_time,
            )
            return '', ''
        delta = 0.05 + attempts * 0.1
        total_wait_time += delta
        time.sleep(delta)
        attempts += 1
    return '', ''


def _assert_task_succeeded(task: Dict[str, str], timeout: int = DEFAULT_TASK_TIMEOUT) -> None:
    assert _wait_for_task(task, timeout=timeout)[0] == 'succeeded'


def _assert_task_not_failed(task: Dict[str, str], timeout: int = DEFAULT_TASK_TIMEOUT) -> None:
    assert _wait_for_task(task, timeout=timeout)[0] != 'failed'
