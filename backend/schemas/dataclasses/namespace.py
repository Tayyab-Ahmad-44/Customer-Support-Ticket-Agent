
from enum import Enum


class NamespaceEnum(str, Enum):
    technical = "technical"
    billing = "billing"
    security = "security"
    general = "general"
