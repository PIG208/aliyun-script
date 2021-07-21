from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class EipConfiguration:
    RegionId: str
    BandWidth: int
    InstanceChargeType: str
    InternetChargeType: str
    ISP: str


@dataclass
class EipInstance:
    AllocationId: str
    IpAddress: str
    Bandwidth: Optional[int] = None
    InternetChargeType: Optional[str] = None
    IsSupportUnassociate: Optional[bool] = None


@dataclass
class EcsInstance:
    InstanceId: str
    InstanceName: str
    Status: str
    RegionId: str
    EipAddress: Optional[EipInstance] = None


class EipStatus(Enum):
    available = "Available"
    in_use = "InUse"
    associating = "Associating"
    unassociating = "Unassociating"


class EcsStatus(Enum):
    running = "Running"
    stopped = "Stopped"
    stopping = "Stopping"
    starting = "Starting"
    pending = "Pending"
