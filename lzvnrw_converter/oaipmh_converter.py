"""
Implementation of the metadata converter-interface for 
OAI-PMH repositories.
"""

import xmltodict
from dcm_common.util import NestedDict

from dcm_metadata_converter.converter_interface import ConverterInterface


class OAIPMHMetadataConverter(ConverterInterface):
    """
    Implementation of the source metadata to dict-converter based on the
    ConverterInterface.
    """

    _SPECVERSION = (0, 3, 1, "")
    CONVERTER_TAG = "OAI-PMH Metadata Converter"

    def get_dict(self, source_metadata: str) -> NestedDict:
        full_input = xmltodict.parse(source_metadata)

        return full_input["OAI-PMH"]["GetRecord"]["record"]
    