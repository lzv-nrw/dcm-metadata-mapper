"""
Test suite for the OAI-PMH-specific implementation of the
metadata mapper.
"""
import pytest
from lzvnrw_converter.oaipmh_converter import OAIPMHMetadataConverter
from dcm_metadata_mapper.mapper_factory import\
    generate_metadata_mapper_class, LINEAR_MAP_STANDARD


def count_length(source_dict: dict) -> int:
    """
    Helper function to count the length of all strings in the metadata
    """
    total_length = 0
    for key in source_dict["metadata"]["oai_dc:dc"]:
        values = source_dict["metadata"]["oai_dc:dc"][key]
        if isinstance(values, str):
            values = [values]
        for value in values:
            if value is not None:
                total_length += len(value)
    return total_length


@pytest.fixture(name="minimal_source_dict")
def get_minimal_source_dict():
    """
    Returns a dict from a given minimal XML for testing the mapper.
    This example is miami-specific.
    """
    some_converter = OAIPMHMetadataConverter()

    return some_converter.get_dict(
"""<OAI-PMH>
    <responseDate>2023-09-07T08:26:19Z</responseDate>
    <request>https://repositorium.uni-muenster.de/oai/miami</request>
    <GetRecord>
        <record>
            <header>
                <identifier>oai:wwu.de:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</identifier>
            </header>
            <metadata>
                <oai_dc:dc>
                    <dc:title>This is a test</dc:title>
                    <dc:creator>Mustermann, M.</dc:creator>
                    <dc:creator>Mustermann, E.</dc:creator>
                    <dc:identifier />
                    <dc:identifier>
                        https://nbn-resolving.org/urn:nbn:de:hbz:x-xxxxxxxxxxx
                    </dc:identifier>
                    <dc:identifier>urn:nbn:de:hbz:x-xxxxxxxxxxx</dc:identifier>
                    <dc:identifier>10.11111/xxxxxxxxxxx</dc:identifier>
                    <dc:identifier>
                        https://repositorium.uni-muenster.de/transfer/miami/xxxxxxxxxxx
                    </dc:identifier>
                </oai_dc:dc>
            </metadata>
        </record>
    </GetRecord>
</OAI-PMH>
"""
    )


@pytest.fixture(name="deleted_record_dict")
def get_deleted_record_dict():
    """
    Returns a dict from a deleted record.
    """
    some_converter = OAIPMHMetadataConverter()

    return some_converter.get_dict(
"""<OAI-PMH>
<GetRecord>
    <record>
        <header status="deleted">
            <identifier>oai:id0</identifier>
        </header>
    </record>
</GetRecord>
</OAI-PMH>
"""
    )


@pytest.fixture(name="user_linear_map")
def extend_linear_map():
    """
    Returns a dict with a user linear map.
    The entry 'dc-terms-identifier' differs from the standard linear map
    in order to assert proper replacement when use_standard_linear_map is True.
    """
    return {
        "source-organization": {
            "value": "some organization"
        },
        "dc-terms-identifier": {
            "path": ["metadata", "oai_dc:dc", "dc:identifier"]
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


@pytest.fixture(name="user_mapper_only")
def get_some_mapper_user_only(user_linear_map):
    """Returns a user mapper."""
    return generate_metadata_mapper_class(
        mapper_tag="Some Metadata Mapper",
        spec_version = (0, 3, 2, ""),
        linear_map=user_linear_map,
        _nonlinear_map=None,
        use_standard_linear_map=False
    )()


@pytest.fixture(name="user_mapper_with_standard")
def get_some_mapper_extended_standard(user_linear_map):
    """Returns a user mapper."""
    return generate_metadata_mapper_class(
        mapper_tag="Some Metadata Mapper using the standard linear map",
        spec_version = (0, 3, 2, ""),
        linear_map=user_linear_map,
        _nonlinear_map=None,
        use_standard_linear_map=True
    )()


@pytest.fixture(name="user_mapper_only_standard")
def get_some_mapper():
    """Returns a user mapper."""
    return generate_metadata_mapper_class(
        mapper_tag="Some Metadata Mapper using only the standard linear map",
        spec_version = (0, 3, 2, ""),
        linear_map=None,
        _nonlinear_map=None,
        use_standard_linear_map=True
    )()


def test_get_specversion(user_mapper_only):
    """
    Test the public get-method for _SPECVERSION.
    """
    mapper_specversion = user_mapper_only.get_specversion()
    assert all(isinstance(n, int) for n in mapper_specversion[0:3])
    assert isinstance(mapper_specversion[3], str)
    assert mapper_specversion == (0, 3, 2, "")


def test_mapper_tags(
    user_mapper_only,
    user_mapper_with_standard,
    user_mapper_only_standard
):
    """
    Assert that the mapper tags are as expected.
    """

    assert user_mapper_only.MAPPER_TAG == "Some Metadata Mapper"
    assert user_mapper_with_standard.MAPPER_TAG ==\
        "Some Metadata Mapper using the standard linear map"
    assert user_mapper_only_standard.MAPPER_TAG ==\
        "Some Metadata Mapper using only the standard linear map"


def test_linear_maps(
    user_linear_map,
    user_mapper_only,
    user_mapper_with_standard,
    user_mapper_only_standard
):
    """
    Assert that the linear maps of the different mappers are as expected.
    """
    # user_mapper_only has simply user_linear_map
    assert user_mapper_only.linear_map == user_linear_map
    # user_mapper_with_standard has the union
    # of LINEAR_MAP_STANDARD and user_linear_map
    assert user_mapper_with_standard.linear_map ==\
        LINEAR_MAP_STANDARD | user_linear_map
    # user_mapper_only_standard has simply LINEAR_MAP_STANDARD
    assert user_mapper_only_standard.linear_map == LINEAR_MAP_STANDARD


def test_key_existence_in_linear_map(
    minimal_source_dict,
    user_mapper_only,
    user_mapper_with_standard,
    user_mapper_only_standard
):
    """
    Assert that the expected outputs are returned depending on
    whether a key exists in the linear map.
    """

    result_user_mapper_only = user_mapper_only.get_metadata(
        key="DC-Creator",
        source_metadata=minimal_source_dict
    )
    result_user_mapper_with_standard = user_mapper_with_standard.get_metadata(
        key="DC-Creator",
        source_metadata=minimal_source_dict
    )
    result_user_mapper_only_standard = user_mapper_only_standard.get_metadata(
        key="DC-Creator",
        source_metadata=minimal_source_dict
    )

    # The key does not exist in the user linear map.
    assert result_user_mapper_only is None
    # result_user_mapper_with_standard and result_user_mapper_only_standard
    # should return exactly the same result.
    assert result_user_mapper_with_standard ==\
        result_user_mapper_only_standard
    #
    assert isinstance(result_user_mapper_with_standard, list)
    assert len(result_user_mapper_with_standard) == 2
    assert result_user_mapper_with_standard[0] == "Mustermann, M."
    assert result_user_mapper_with_standard[1] == "Mustermann, E."


def test_replacement_in_linear_map(
    minimal_source_dict,
    user_mapper_only,
    user_mapper_with_standard,
    user_mapper_only_standard
):
    """
    Assert that the user input for the linear map overwrites
    the standard value when the argument use_standard_linear_map is True.
    From an input dict, assert that the expected outputs are returned.
    """

    result_user_mapper_only = user_mapper_only.get_metadata(
        key="DC-Terms-Identifier",
        source_metadata=minimal_source_dict
    )
    result_user_mapper_with_standard = user_mapper_with_standard.get_metadata(
        key="DC-Terms-Identifier",
        source_metadata=minimal_source_dict
    )
    result_user_mapper_only_standard = user_mapper_only_standard.get_metadata(
        key="DC-Terms-Identifier",
        source_metadata=minimal_source_dict
    )

    # user_mapper_only and user_mapper_with_standard
    # should return exactly the same result.
    assert result_user_mapper_only == result_user_mapper_with_standard
    #
    assert len(result_user_mapper_only) == 5
    assert len(result_user_mapper_with_standard) == 5
    assert len(result_user_mapper_only_standard) == 3


def test_return_none(
    minimal_source_dict,
    user_mapper_only,
    user_mapper_only_standard
):
    """From an input dict, assert that the expected outputs are returned."""

    # Source-Organization
    result_user_mapper_only = user_mapper_only.get_metadata(
        "Source-Organization",
        minimal_source_dict
    )
    result_user_mapper_only_standard = user_mapper_only_standard.get_metadata(
        "Source-Organization",
        minimal_source_dict
    )
    assert result_user_mapper_only == "some organization"
    assert result_user_mapper_only_standard is None

    # transfer-urls
    result_user_mapper_only = user_mapper_only.get_metadata(
        "transfer-urls", minimal_source_dict
    )
    result_user_mapper_only_standard = user_mapper_only_standard.get_metadata(
        "transfer-urls", minimal_source_dict
    )
    assert result_user_mapper_only ==\
        ["https://repositorium.uni-muenster.de/transfer/miami/xxxxxxxxxxx"]
    assert result_user_mapper_only_standard is None

    # Unknown-Key
    result_user_mapper_only = user_mapper_only.get_metadata(
        "Unknown-Key",
        minimal_source_dict
    )
    result_user_mapper_only_standard = user_mapper_only_standard.get_metadata(
        "Unknown-Key",
        minimal_source_dict
    )
    assert result_user_mapper_only is None
    assert result_user_mapper_only_standard is None


def test_get_metadata_unknown_key(minimal_source_dict, user_mapper_only):
    """
    Ensure that get_metadata returns None
    for a key that is not included in any mapping.
    """
    result_unknown_key = \
        user_mapper_only.get_metadata("Unknown-Key", minimal_source_dict)

    assert result_unknown_key is None


def test_map_nonlinear(minimal_source_dict, user_linear_map):
    """
    Ensure the nonlinear mapping for a specific key.
    """

    user_mapper = generate_metadata_mapper_class(
        linear_map=user_linear_map,
        _nonlinear_map={
            "length-metadata-strings": count_length
        },
        mapper_tag="Some Metadata Mapper",
        spec_version = (0, 3, 2, "")
    )()

    result = user_mapper.get_metadata(
        key="length-metadata-strings",
        source_metadata=minimal_source_dict
    )

    assert result == 207
    assert user_mapper.MAPPER_TAG == "Some Metadata Mapper"


def test_map_nonlinear_replaces_linear(
    minimal_source_dict,
    user_linear_map
):
    """
    Ensure that the keys of the nonlinear mapping replace
    any value given in the linear mapping.
    """
    user_mapper = generate_metadata_mapper_class(
        linear_map=user_linear_map,
        _nonlinear_map={
            "dc-creator": count_length
        },
        mapper_tag="Some Metadata Mapper",
        spec_version = (0, 3, 2, "")
    )()

    result = user_mapper.get_metadata(
        key="DC-Creator",
        source_metadata=minimal_source_dict
    )

    assert result == 207
    assert user_mapper.MAPPER_TAG == "Some Metadata Mapper"


def test_deleted_record(deleted_record_dict, user_mapper_with_standard):
    """
    Ensure the deleted record is mapped as expected without errors.
    """

    result_source_organization = user_mapper_with_standard.get_metadata(
        key="source-organization",
        source_metadata=deleted_record_dict
    )
    result_origin_system_identifier = user_mapper_with_standard.get_metadata(
        key="origin-system-identifier",
        source_metadata=deleted_record_dict
    )
    result_external_identifier = user_mapper_with_standard.get_metadata(
        key="external-identifier",
        source_metadata=deleted_record_dict
    )
    result_dc_terms_identifier = user_mapper_with_standard.get_metadata(
        key="dc-terms-identifier",
        source_metadata=deleted_record_dict
    )
    result_transfer_urls = user_mapper_with_standard.get_metadata(
        key="transfer-urls",
        source_metadata=deleted_record_dict
    )
    result_unknown_key = user_mapper_with_standard.get_metadata(
        key="unknown-key",
        source_metadata=deleted_record_dict
    )

    assert result_source_organization == "some organization"
    assert result_origin_system_identifier == "oai"
    assert result_external_identifier == "id0"
    assert result_dc_terms_identifier is None
    assert result_transfer_urls is None
    assert result_unknown_key is None
