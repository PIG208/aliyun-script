import argparse

from aliyun_scripts.lib.actions import shutdown_ecs, start_ecs
from aliyun_scripts.lib.instances import EcsStatus
from aliyun_scripts.lib.utils import (
    get_client_config_and_ecs,
    get_print,
    wait_ecs_status,
)
from aliyun_scripts.tools.eip_tool import (
    load_config_and_unbind_allocate_and_bind_new_eip,
    unbind_release,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Manage the ecs using aliyun API")

    signals = ["stop", "start", "rebind", "ip", "status", "release"]
    parser.add_argument(
        "-s",
        "--signal",
        help="Specified the action to be taken",
        choices=signals,
        required=True,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show verbose output"
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Disable output")

    return parser.parse_args()


def main():
    args = parse_args()
    _print = get_print(args.quiet)

    client, _, ecs = get_client_config_and_ecs()

    if args.signal == "stop":
        _print("+ Shutting down the ecs")
        shutdown_ecs(client, ecs, "StopCharging")
        wait_ecs_status(
            client,
            ecs,
            EcsStatus.stopped,
            lambda: print("Waiting the ecs to stop..."),
            interval=5,
        )
        _print("Successfully stopped the ecs")
    elif args.signal == "start":
        _print("+ Starting the ecs")
        start_ecs(client, ecs)
        wait_ecs_status(
            client,
            ecs,
            EcsStatus.running,
            lambda: print("Waiting the ecs to start running..."),
        )
        _print("Successfully started the ecs")
    elif args.signal == "rebind":
        _print("+ Rebinding the ecs")
        load_config_and_unbind_allocate_and_bind_new_eip(
            args.verbose, args.quiet, True, True
        )
    elif args.signal == "ip":
        if ecs.EipAddress is not None:
            _print(
                f"The ip address of {ecs.InstanceId} ({ecs.InstanceName}) is:\n{ecs.EipAddress.IpAddress}"
            )
        else:
            _print("No eip binded")
    elif args.signal == "status":
        _print(f"The status of {ecs.InstanceId} ({ecs.InstanceName}) is:\n{ecs.Status}")
    elif args.signal == "release":
        unbind_release(client, ecs, True, args.verbose, args.quiet)


if __name__ == "__main__":
    main()
