"""
Implementation of the metadata mapper-interface.
"""
import re
from typing import Any, Optional, Callable

from dcm_common.util import NestedDict, value_from_dict_path

from dcm_metadata_mapper.mapper_interface import MapperInterface


def generate_metadata_mapper_class(
    mapper_tag: str,
    spec_version: tuple[int, int, int, str],
    linear_map: Optional[dict[str, dict[str, Any]]],
    _nonlinear_map: Optional[dict[str, Callable[..., Any]]] = None,
    use_standard_linear_map: bool = False
) -> type[MapperInterface]:
    """
    Interface factory to dynamically create python mapper-classes.

    Keyword arguments:
    mapper_tag -- the string tag for the mapper object
    spec_version -- version of a specification with which a class
                    that implements this interface is compatible;
                    Expected format: 4-tuple of
                    (major:int, minor:int, patch:int, label:str)
    linear_map -- the linear map as a nested dict. Possible keys:   
                  "value": return the value of this key.
                  "path": navigate through the source_metadata to get the value.
                  "post-process": perform post-processing of the value
                                  defined using the "path" key.
                                  It should handle None values,
                                  which will otherwise lead to a TypeError.
                  (see LINEAR_MAP_STANDARD)
    _nonlinear_map -- the nonlinear map as dict of key-function pairs
    use_standard_linear_map -- whether to extend the provided linear_map
                               by using the LINEAR_MAP_STANDARD
                               (default False)
    """

    class MetadataMapper(MapperInterface):
        """
        Factory for metadata mappers.
        """

        _SPECVERSION = spec_version
        MAPPER_TAG = mapper_tag

        def __init__(self) -> None:

            self.use_standard_linear_map = use_standard_linear_map

            # Define the linear map
            if linear_map is not None:
                if self.use_standard_linear_map:
                    # Get the union of the two maps.
                    # The user input should be the right-hand operand.
                    self.linear_map = LINEAR_MAP_STANDARD | linear_map
                else:
                    self.linear_map = linear_map
            else:
                if self.use_standard_linear_map:
                    self.linear_map = LINEAR_MAP_STANDARD.copy()
                else:
                    self.linear_map = {}

            # Define the nonlinear map
            if _nonlinear_map is not None:
                self._nonlinear_map = _nonlinear_map
            else:
                self._nonlinear_map = {}

            # Delete all keys included in the _nonlinear_map
            # from the linear map
            for key in self._nonlinear_map.keys():
                if key in self.linear_map:
                    del self.linear_map[key]

        def get_metadata(
            self,
            key: str,
            source_metadata: NestedDict
        ) -> Optional[str | list[str]]:

            if key.lower() in self.linear_map:
                # linear map-section
                value = self._get_metadata_linear(
                    key.lower(),
                    source_metadata
                )
            elif key.lower() in self._nonlinear_map:
                # nonlinear map-section
                value = self._get_metadata_nonlinear(
                    key.lower(),
                    source_metadata
                )
            else:
                return None
            return value

        def _get_metadata_linear(
            self,
            key_lower: str,
            source_metadata: NestedDict
        ) -> Optional[str | list[str]]:
            """
            Get the metadata based on the linear map, which is a NestedDict.
            If the "value" key exists, return its value.
            Otherwise, use the value of the "path" key to navigate
            through the NestedDict of source_metadata,
            e.g., ["header", "identifier"].
            Optional, perform post-processing as instructed
            in the "post-process" key, e.g., lambda pp: pp.rsplit(":", 1)[1].
            """

            # default to those entries already existing in source_metadata
            # if static value, return that
            if "value" in self.linear_map[key_lower]:
                return self.linear_map[key_lower]["value"]

            # otherwise use path through nested dict as specified in map
            value = value_from_dict_path(
                nesteddict=source_metadata,
                path=self.linear_map[key_lower]["path"]
            )

            # perform post-processing if available
            if "post-process" in self.linear_map[key_lower]:
                value = self.linear_map[key_lower]["post-process"](value)

            return value

        def _get_metadata_nonlinear(
            self,
            key_lower: str,
            source_metadata: NestedDict
        ) -> Optional[str | list[str]]:
            return self._nonlinear_map[key_lower](source_metadata)

    MetadataMapper.__doc__ = mapper_tag
    return MetadataMapper

# LINEAR_MAP_STANDARD defines a dictionary with common key-value pairs
# for pre-filling the linear map.
# FIXME:
# The keys 'source-organization' and 'transfer-urls'
# should be included in the maps during the object instantiation.
# Missing: 'DC-Terms-Rights', 'DC-Terms-License', 'DC-Terms-Access-Rights',
# 'Embargo-Enddate', 'DC-Terms-Rights-Holder', 'Preservation-Level'.
# Filled by builder: 'Payload-Oxum', 'Bagging-DateTime'.
# Filled by cli/dcm: 'Bag-Software-Agent', 'BagIt-Profile-Identifier',
# 'BagIt-Payload-Profile-Identifier'.
LINEAR_MAP_STANDARD: dict[str, dict[str, Any]] = {
    "origin-system-identifier": {
        "path": ["header", "identifier"],
        "post-process": lambda pp: None if pp is None else pp.rsplit(":", 1)[0]
    },
    "external-identifier": {
        "path": ["header", "identifier"],
        "post-process": lambda pp: None if pp is None else pp.rsplit(":", 1)[1]
    },
    "dc-creator": {
        "path": ["metadata", "oai_dc:dc", "dc:creator"]
    },
    "dc-title": {
        "path": ["metadata", "oai_dc:dc", "dc:title"]
    },
    "dc-rights": {
        "path": ["metadata", "oai_dc:dc", "dc:rights"]
    },
    "dc-terms-identifier": {
        "path": ["metadata", "oai_dc:dc", "dc:identifier"],
        "post-process": (lambda pp: None if pp is None else\
            [
                entry for entry in pp
                    if entry is not None and re.search(
                        r"10\.\d{4,9}\/[-._;()/:A-Z0-9]+|urn:nbn",
                        entry,
                        re.IGNORECASE
                    )
            ]
        )
    }
}
