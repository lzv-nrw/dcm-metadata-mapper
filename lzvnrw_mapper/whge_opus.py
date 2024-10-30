"""
This module defines the mapper class for the whge-OPUS repository.
"""

from dcm_metadata_mapper.mapper_factory import\
    generate_metadata_mapper_class, LINEAR_MAP_STANDARD


# Define the linear map
# Extend the standard linear map with the hbz-OPUS-specific key-pair values.
# For common keys, the right-hand operand wins.
whge_opus_linear_map = LINEAR_MAP_STANDARD | {
    "dc-title": {
        "path": ["metadata", "oai_dc:dc", "dc:title", "#text"]
    },
    "source-organization": {
        "value": "https://d-nb.info/gnd/1022953834"
    },
    "transfer-urls": {
        "path": ["metadata", "oai_dc:dc", "dc:identifier"],
        "post-process": (lambda pp: None if pp is None else\
            [
                element
                for element in pp
                if element is not None and\
                    "https://whge.opus.hbz-nrw.de/files/" in element
            ])
    }
}

# Generate the mapper class using the factory function
WhgeOpusMetadataMapper = generate_metadata_mapper_class(
    mapper_tag="Whge OPUS Metadata Mapper",
    spec_version = (0, 3, 2, ""),
    linear_map=whge_opus_linear_map
)
