import json
from dataclasses import asdict
from typing import List, Optional, Union

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.AllocateEipAddressRequest import (
    AllocateEipAddressRequest,
)
from aliyunsdkecs.request.v20140526.AssociateEipAddressRequest import (
    AssociateEipAddressRequest,
)
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import (
    DescribeInstancesRequest,
)
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest
from aliyunsdkecs.request.v20140526.UnassociateEipAddressRequest import (
    UnassociateEipAddressRequest,
)
from aliyunsdkvpc.request.v20160428.DescribeEipAddressesRequest import (
    DescribeEipAddressesRequest,
)
from aliyunsdkvpc.request.v20160428.ReleaseEipAddressRequest import (
    ReleaseEipAddressRequest,
)
from typing_extensions import Literal

from aliyun_scripts.lib.exceptions import AllocationFailureError, UnbindFailureError
from aliyun_scripts.lib.instances import (
    EcsInstance,
    EcsStatus,
    EipConfiguration,
    EipInstance,
    EipStatus,
)
from aliyun_scripts.lib.utils import acs_req, p


def bind_eip_to_ecs(client: AcsClient, eip: EipInstance, ecs: EcsInstance) -> str:
    return acs_req(
        client,
        AssociateEipAddressRequest(),
        {
            "InstanceId": ecs.InstanceId,
            "AllocationId": eip.AllocationId,
            "RegionId": ecs.RegionId,
        },
    )


def unbind_eip_from_ecs(
    client: AcsClient, ecs: EcsInstance, eip: Optional[EipInstance] = None
) -> EipInstance:
    if eip is None and (ecs.EipAddress is None or ecs.EipAddress.AllocationId is None):
        raise UnbindFailureError("There is no existing eip to be unbinded")
    eip = eip if eip is not None else ecs.EipAddress
    allocation_id = eip.AllocationId if eip is not None else ecs.EipAddress.AllocationId
    acs_req(
        client,
        UnassociateEipAddressRequest(),
        {
            "InstanceId": ecs.InstanceId,
            "AllocationId": allocation_id,
            "RegionId": ecs.RegionId,
        },
    )
    return eip


def get_available_ecs(
    client: AcsClient,
    instance_id: Optional[str] = None,
    status: Optional[EcsStatus] = None,
) -> List[EcsInstance]:
    params = {
        "InstanceIds": [instance_id],
        "Status": status.value if status is not None else None,
    }
    if instance_id is None:
        del params["InstanceIds"]
    if status is None:
        del params["Status"]
    return [
        EcsInstance(
            instance["InstanceId"],
            instance["InstanceName"],
            instance["Status"],
            instance["RegionId"],
            (
                lambda eip: EipInstance(
                    eip["AllocationId"],
                    eip["IpAddress"],
                    eip["Bandwidth"],
                    eip["InternetChargeType"],
                    eip["IsSupportUnassociate"],
                )
                if eip is not None and len(eip["AllocationId"]) > 0
                else None
            )(instance.get("EipAddress")),
        )
        for instance in acs_req(client, DescribeInstancesRequest(), params,)[
            "Instances"
        ]["Instance"]
    ]


def get_available_eip(
    client: AcsClient,
    status: Optional[EipStatus] = None,
    region_id: Optional[str] = None,
    eip: Optional[Union[EipInstance, str]] = None,
) -> List[EipInstance]:
    allocation_id = eip.AllocationId if isinstance(eip, EipInstance) else eip
    params = {
        "Status": status.value,
        "RegionId": region_id,
        "AllocationId": allocation_id,
    }
    if allocation_id is None:
        del params["AllocationId"]
    return [
        EipInstance(
            instance["AllocationId"],
            instance["IpAddress"],
            instance["Bandwidth"],
            instance["InternetChargeType"],
            instance.get("IsSupportUnassociate"),
        )
        for instance in acs_req(client, DescribeEipAddressesRequest(), params)[
            "EipAddresses"
        ]["EipAddress"]
    ]


def allocate_eip(
    client: AcsClient, config: EipConfiguration, verbose: bool
) -> EipInstance:
    result = acs_req(
        client,
        AllocateEipAddressRequest(),
        asdict(config),
    )
    try:
        return EipInstance(
            IpAddress=result["EipAddress"], AllocationId=result["AllocationId"]
        )
    except KeyError:
        p(verbose, result)
        raise AllocationFailureError("Cannot allocate a new eip, see the result above")


def release_eip(client: AcsClient, eip: Union[EipInstance, str]) -> str:
    allocation_id = eip.AllocationId if isinstance(eip, EipInstance) else eip
    return acs_req(client, ReleaseEipAddressRequest(), {"AllocationId": allocation_id})


def shutdown_ecs(
    client: AcsClient,
    ecs: Union[EcsInstance, str],
    stopped_mode: Literal["StopCharging", "KeepCharing"],
    force_stop: bool = False,
) -> str:
    instance_id = ecs.InstanceId if isinstance(ecs, EcsInstance) else ecs
    return acs_req(
        client,
        StopInstanceRequest(),
        {
            "InstanceId": instance_id,
            "StoppedMode": stopped_mode,
            "ForceStop": force_stop,
        },
    )


def start_ecs(
    client: AcsClient,
    ecs: Union[EcsInstance, str],
) -> str:
    instance_id = ecs.InstanceId if isinstance(ecs, EcsInstance) else ecs
    return acs_req(
        client,
        StartInstanceRequest(),
        {
            "InstanceId": instance_id,
        },
    )
