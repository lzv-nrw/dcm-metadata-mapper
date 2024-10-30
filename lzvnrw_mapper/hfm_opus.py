"""
This module defines the mapper class for the hfm-OPUS repository.
"""

from dcm_metadata_mapper.mapper_factory import\
    generate_metadata_mapper_class, LINEAR_MAP_STANDARD


# Define the linear map
# Extend the standard linear map with the hbz-OPUS-specific key-pair values.
# For common keys, the right-hand operand wins.
hfm_opus_linear_map = LINEAR_MAP_STANDARD | {
    "dc-title": {
        "path": ["metadata", "oai_dc:dc", "dc:title", "#text"]
    },
    "source-organization": {
        "value": "https://d-nb.info/gnd/5073685-1"
    },
    "transfer-urls": {
        "path": ["metadata", "oai_dc:dc", "dc:identifier"],
        "post-process": (lambda pp: None if pp is None else\
            [
                element
                for element in pp
                if element is not None and\
                    "https://opus.hfm-detmold.de/files/" in element
            ])
    }
}

# Generate the mapper class using the factory function
HfmOpusMetadataMapper = generate_metadata_mapper_class(
    mapper_tag="Hfm OPUS Metadata Mapper",
    spec_version = (0, 3, 2, ""),
    linear_map=hfm_opus_linear_map
)
