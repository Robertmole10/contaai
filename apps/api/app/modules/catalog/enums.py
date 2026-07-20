from __future__ import annotations

from enum import Enum


class ProductType(str, Enum):
    """Type of catalog item."""

    PRODUCT = "product"
    SERVICE = "service"


class UnitDimension(str, Enum):
    """
    General measurement dimension.

    This allows units such as pieces, hours, kilograms, litres,
    metres and square metres to be grouped consistently.
    """

    COUNT = "count"
    TIME = "time"
    MASS = "mass"
    LENGTH = "length"
    AREA = "area"
    VOLUME = "volume"
    OTHER = "other"