"""
This module defines the mapper class for the miami repository.
"""

from dcm_metadata_mapper.mapper_factory import\
    generate_metadata_mapper_class, LINEAR_MAP_STANDARD


# Define the linear map
# Extend the standard linear map with the miami-specific key-pair values.
# For common keys, the right-hand operand wins.
miami_linear_map = LINEAR_MAP_STANDARD | {
    "source-organization": {
        "value": "https://d-nb.info/gnd/5091030-9"
    },
    "transfer-urls": {
        "path": ["metadata", "oai_dc:dc", "dc:identifier"],
        "post-process": (lambda pp: None if pp is None else\
            [
                element for element in pp
                if element is not None and\
                    "https://repositorium.uni-muenster.de/transfer/" in element
            ]
        )
    }
}

# Generate the mapper class using the factory function
MiamiMetadataMapper = generate_metadata_mapper_class(
    mapper_tag="Miami Metadata Mapper",
    spec_version = (0, 3, 2, ""),
    linear_map=miami_linear_map
)
