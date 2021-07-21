import argparse
from dataclasses import asdict
from typing import Callable, Optional

from aliyunsdkcore.client import AcsClient

from aliyun_scripts.lib.actions import (
    allocate_eip,
    bind_eip_to_ecs,
    get_available_eip,
    release_eip,
    unbind_eip_from_ecs,
)
from aliyun_scripts.lib.exceptions import UnbindFailureError
from aliyun_scripts.lib.instances import EcsInstance, EipConfiguration, EipStatus
from aliyun_scripts.lib.utils import (
    get_client_config_and_ecs,
    get_print,
    p,
    wait_eip_status,
)


def unbind_release(
    client: AcsClient,
    target_ecs: EcsInstance,
    release_old_eip: bool,
    verbose: bool,
    quiet: bool,
):
    _print = get_print(quiet)
    try:
        _print("+ Trying to unbind currently binded eip")
        eip = unbind_eip_from_ecs(client, target_ecs)
        wait_eip_status(
            client,
            eip,
            EipStatus.available,
            target_ecs.RegionId,
            lambda: _print("Waiting for the eip to be unbinded..."),
        )
        _print("Successfully unbinded the eip")
        p(verbose, asdict(eip))
        if release_old_eip:
            _print("+ Trying to release the unbinded eip")
            release_eip(client, eip)
            _print("Successfully relased the eip")
        else:
            _print("Not going to release the old eip by configuration")
    except UnbindFailureError:
        _print("No eip to be unbinded, continuing...")


def unbind_allocate_and_bind_new_eip(
    client: AcsClient,
    target_ecs: EcsInstance,
    eip_config: EipConfiguration,
    verbose: bool,
    quiet: bool,
    release_old_eip: bool,
    allocate_new_eip: bool,
) -> Optional[EcsInstance]:
    _print = get_print(quiet)

    # See if there is already an available eip
    _print("+ Finding existing available eips")
    eip_list = get_available_eip(client, EipStatus.available, target_ecs.RegionId)
    new_eip = None

    if len(eip_list) > 0:
        _print("Available eip found, going to use it without creating a new one")
        new_eip = eip_list[0]
        p(verbose, asdict(new_eip))
    else:
        _print("No available eip found")
        if not allocate_new_eip:
            _print("Cannot create new eip by configuration, exitting now...")
            return None
        _print("+ Going to create a new eip with the following configuration")
        p(verbose, asdict(eip_config))
        new_eip = allocate_eip(client, eip_config, verbose)
        _print("Allocated new eip")
        p(verbose, new_eip)

    # If there is an eip currently binded, we unbind it first
    unbind_release(client, target_ecs, release_old_eip, verbose, quiet)

    _print("+ Trying to bind the new eip")
    bind_eip_to_ecs(client, new_eip, target_ecs)
    wait_eip_status(
        client,
        new_eip,
        EipStatus.in_use,
        target_ecs.RegionId,
        lambda: _print("Waiting for the eip to be binded..."),
    )
    _print(
        f"Binded eip {new_eip.AllocationId} ({new_eip.IpAddress}) to ecs {target_ecs.InstanceId} ({target_ecs.InstanceName})"
    )
    return target_ecs


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show verbose output"
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Disable output")

    return parser.parse_args()


def load_config_and_unbind_allocate_and_bind_new_eip(
    verbose: bool,
    quiet: bool,
    release_old_eip: bool = True,
    allocate_new_eip: bool = True,
) -> Optional[EcsInstance]:
    _print = get_print(quiet)

    client, config, target_ecs = get_client_config_and_ecs()
    if target_ecs is None:
        _print("Cannot find the target ecs instance, exitting...")
        return None
    _print("Ecs instance found")
    p(verbose, asdict(target_ecs))
    eip_config = EipConfiguration(
        RegionId=target_ecs.RegionId,
        BandWidth=config["BandWidth"],
        InstanceChargeType=config["InstanceChargeType"],
        InternetChargeType=config["InternetChargeType"],
        ISP=config["ISP"],
    )
    unbind_allocate_and_bind_new_eip(
        client,
        target_ecs,
        eip_config,
        not quiet and verbose,
        quiet,
        release_old_eip,
        allocate_new_eip,
    )


def main():
    args = parse_args()
    load_config_and_unbind_allocate_and_bind_new_eip(
        args.verbose, args.quiet, True, True
    )


if __name__ == "__main__":
    main()
