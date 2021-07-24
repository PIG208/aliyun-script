import json
import os
import pprint
from enum import Enum
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from aliyunsdkcore.client import AcsClient

from aliyun_scripts.lib.instances import EcsInstance, EcsStatus, EipInstance, EipStatus

current_dir = os.path.dirname(os.path.abspath(__file__))
pp = pprint.PrettyPrinter(indent=4)
SECRETS = os.path.expanduser("~/secrets.json")
CONFIG = os.path.expanduser("~/config.json")


def p(verbose, *args, **kwargs):
    if verbose:
        pp.pprint(*args, **kwargs)


def update_config(secrets: Optional[str], config: Optional[str]) -> None:
    global SECRETS, CONFIG

    if secrets is not None:
        SECRETS = secrets
    if config is not None:
        CONFIG = config


def acs_req(client: AcsClient, r: Any, params: Dict[str, Any] = {}) -> dict:
    for k, v in params.items():
        r.add_query_param(k, v)
    return json.loads(client.do_action_with_exception(r).decode())


def get_client_and_config() -> Tuple[AcsClient, dict]:
    access_info = json.load(open(SECRETS))
    config = json.load(open(CONFIG))
    client = AcsClient(
        ak=access_info["accessKey_id"],
        secret=access_info["accessKey_secret"],
        region_id=access_info["region_id"],
    )
    return client, config


def get_client_config_and_ecs() -> Tuple[AcsClient, dict, Optional[EcsInstance]]:
    from aliyun_scripts.lib.actions import get_available_ecs

    client, config = get_client_and_config()
    ecs_list = get_available_ecs(client, config["Target"])

    if len(ecs_list) > 0:
        return client, config, ecs_list[0]
    else:
        return client, config, None


def wait_status(
    get_func: Callable[[Enum], List],
    till_status: EipStatus,
    cb: Optional[Callable[[], Any]] = None,
    interval: int = 2,
    max_retries: int = 5,
) -> None:
    remaining_retries = max_retries
    while len(get_func(till_status)) == 0:
        if remaining_retries == 0:
            raise Exception("Exceeded maximum retries")
        remaining_retries -= 1
        if cb is not None:
            cb()
        sleep(interval)


def wait_eip_status(
    client: AcsClient,
    eip: EipInstance,
    till_status: EipStatus,
    region_id: str,
    cb: Optional[Callable[[], Any]] = None,
    interval: int = 2,
    max_retries: int = 5,
) -> None:
    if eip.AllocationId is None:
        raise ValueError("The eip address needs to have an allocationId")

    from aliyun_scripts.lib.actions import get_available_eip

    def get_func(status: EipInstance) -> List[EipInstance]:
        return get_available_eip(client, status, region_id, eip)

    wait_status(get_func, till_status, cb, interval, max_retries)


def wait_ecs_status(
    client: AcsClient,
    ecs: Union[EcsInstance, str],
    till_status: EcsStatus,
    cb: Optional[Callable[[], Any]] = None,
    interval: int = 2,
    max_retries: int = 5,
) -> None:
    instance_id = ecs.InstanceId if isinstance(ecs, EcsInstance) else ecs
    if instance_id is None:
        raise ValueError("The InstanceId cannot be None")
    from aliyun_scripts.lib.actions import get_available_ecs

    def get_func(status: EipInstance) -> List[EcsInstance]:
        return get_available_ecs(client, instance_id, status)

    wait_status(
        get_func,
        till_status,
        cb,
        interval,
        max_retries,
    )


def get_print(quiet: bool):
    def _print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    return _print
