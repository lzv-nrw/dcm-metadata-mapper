"""
This module contains an interface for the definition of a metadata-
mapping class that is compatible with the lzv.nrw-dcm.
"""

from typing import Optional
import abc

from dcm_common.util import NestedDict


class MapperInterface(metaclass=abc.ABCMeta):
    """
    Interface for the definition of metadata-mapper classes compatible
    with the lzv.nrw-dcm.

    Required properties/methods:
    _SPECVERSION -- property; version of a specification with which a
                    class that implements this interface is compatible;
                    Expected format:
                    4-tuple of (major:int, minor:int, patch:int, label:str)
    MAPPER_TAG -- property; string identifier for an implementation of
                  this interface
    get_specversion -- method; public get-method for _SPECVERSION
    get_metadata -- method; retrieve information on a specific key from
                    a dictionary of source metadata; returns list or None
    """
    # setup requirements for an object to be regarded as implementing
    # the MapperInterface
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "_SPECVERSION")
            and hasattr(subclass, "MAPPER_TAG")
            and hasattr(subclass, "get_specversion")
            and callable(subclass.get_specversion)
            and hasattr(subclass, "get_metadata")
            and callable(subclass.get_metadata)
            or NotImplemented
        )

    # setup checks for missing implementation/definition of properties
    @property
    @abc.abstractmethod
    def _SPECVERSION(self) -> tuple[int, int, int, str]:
        """
        version of a specification with which a class that implements
        this interface is compatible; Expected format:
        4-tuple of (major:int, minor:int, patch:int, label:str)
        """

        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not define property "\
                "self._SPECVERSION"
        )

    @property
    @abc.abstractmethod
    def MAPPER_TAG(self) -> str:
        """String identifier for an implementation of this interface"""
        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not define property "\
                "self.MAPPER_TAG"
        )

    def get_specversion(self) -> tuple[int, int, int, str]:
        """Public get-method for _SPECVERSION."""
        return self._SPECVERSION

    @abc.abstractmethod
    def get_metadata(self, key: str, source_metadata: NestedDict) \
            -> Optional[str | list[str]]:
        """
        Retrieve information on a specific key from a dictionary of
        source metadata.

        Returns list of strings or None.

        Keyword arguments:
        key -- string specifying the target metadata-key
        source_metadata -- dictionary containing the comprehensive
                           source metadata
        """

        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not define method "\
                "self.get_metadata"
        )
