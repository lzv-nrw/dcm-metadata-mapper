"""
This module contains an interface for the definition of a metadata-
to-dict conversion class that can be used to defined such that
its output is compatible with the requirements of the corresponding
mapper class (see dcm_metadata_mapper-package).
"""

import abc

from dcm_common.util import NestedDict


class ConverterInterface(metaclass=abc.ABCMeta):
    """
    This module contains an interface for the definition of a metadata-
    to-dict conversion class that can be used to defined such that
    its output is compatible with the requirements of the corresponding
    mapper class (see dcm_metadata_mapper-package).

    Required properties/methods:
    _SPECVERSION -- property; version of a specification with which a
                    class that implements this interface is compatible;
                    Expected format:
                    4-tuple of (major:int, minor:int, patch:int, label:str)
    CONVERTER_TAG -- property; string identifier for an implementation of
                       this interface
    get_specversion -- method; public get-method for _SPECVERSION
    get_dict -- method; create dictionary of source metadata based on
                string containing metadata in its source format
                (e.g. xml)
    """
    # setup requirements for an object to be regarded as implementing
    # the ConverterInterface
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "_SPECVERSION")
            and hasattr(subclass, "CONVERTER_TAG")
            and hasattr(subclass, "get_specversion")
            and callable(subclass.get_specversion)
            and hasattr(subclass, "get_dict")
            and callable(subclass.get_dict)
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
    def CONVERTER_TAG(self) -> str:
        """String identifier for an implementation of this interface."""
        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not define property "\
                "self.CONVERTER_TAG"
        )

    def get_specversion(self) -> tuple[int, int, int, str]:
        """Public get-method for _SPECVERSION."""
        return self._SPECVERSION

    @abc.abstractmethod
    def get_dict(self, source_metadata: str) -> NestedDict:
        """
        Create dictionary of source metadata based on string containing
        metadata in its source format (e.g. xml).

        Returns dictionary

        Keyword arguments:
        source_metadata -- source metadata in source format
        """

        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not define method "\
                "self.get_dict"
        )
