"""
Test suite for the miami-specific implementation
of the source metadata mapper.
"""
import pytest
from lzvnrw_converter.oaipmh_converter import OAIPMHMetadataConverter
from lzvnrw_mapper.miami import MiamiMetadataMapper


@pytest.fixture(name="minimal_source_dict_miami")
def get_minimal_source_dict_miami():
    """
    Returns a dict from a given minimal XML for testing the miami mapper.
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
                        https://repositorium.uni-muenster.de/transfer/miami/xxxxxxxxxxx.pdf
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


@pytest.fixture(name="miami_mapper")
def get_miami_mapper():
    """Returns a miami mapper."""
    return MiamiMetadataMapper


def test_miami_mapper(
    minimal_source_dict_miami,
    miami_mapper
):
    """
    Test the miami mapper.
    From an input dict, assert that the expected outputs are returned.
    """

    assert miami_mapper().MAPPER_TAG == "Miami Metadata Mapper"

    # DC-Creator
    result_dc_creator = miami_mapper().get_metadata(
        key="DC-Creator",
        source_metadata=minimal_source_dict_miami
    )
    assert isinstance(result_dc_creator, list)
    assert len(result_dc_creator) == 2
    assert result_dc_creator[0] == "Mustermann, M."
    assert result_dc_creator[1] == "Mustermann, E."

    # DC-Title
    result_dc_title = miami_mapper().get_metadata(
        key="DC-Title",
        source_metadata=minimal_source_dict_miami
    )
    assert result_dc_title == "This is a test"

    # DC-Terms-Identifier
    result_dc_terms_id = miami_mapper().get_metadata(
        "DC-Terms-Identifier",
        minimal_source_dict_miami
    )
    assert len(result_dc_terms_id) == 3

    # Origin-System-Identifier
    result_origin_system_identifier = \
        miami_mapper().get_metadata(
            "Origin-System-Identifier",
            minimal_source_dict_miami
        )
    assert result_origin_system_identifier == "oai:wwu.de"

    # External-Identifier
    result_external_identifier = \
        miami_mapper().get_metadata(
            "External-Identifier",
            minimal_source_dict_miami
        )
    assert result_external_identifier \
        == "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

    # Source-Organization
    result_source_organization = \
        miami_mapper().get_metadata(
            "Source-Organization",
            minimal_source_dict_miami
        )
    assert result_source_organization == "https://d-nb.info/gnd/5091030-9"

    # transfer-urls
    result_transfer_urls = \
        miami_mapper().get_metadata(
            "transfer-urls",
            minimal_source_dict_miami
        )
    assert result_transfer_urls ==\
        ["https://repositorium.uni-muenster.de/transfer/miami/xxxxxxxxxxx.pdf"]


def test_get_specversion(miami_mapper):
    """
    Test the public get-method for _SPECVERSION.
    """
    mapper_specversion = miami_mapper().get_specversion()
    assert all(isinstance(n, int) for n in mapper_specversion[0:3])
    assert isinstance(mapper_specversion[3], str)


def test_deleted_record(deleted_record_dict, miami_mapper):
    """
    Ensure the deleted record is mapped as expected without errors.
    """

    result_source_organization = miami_mapper().get_metadata(
        key="source-organization",
        source_metadata=deleted_record_dict
    )
    result_origin_system_identifier = miami_mapper().get_metadata(
        key="origin-system-identifier",
        source_metadata=deleted_record_dict
    )
    result_external_identifier = miami_mapper().get_metadata(
        key="external-identifier",
        source_metadata=deleted_record_dict
    )
    result_transfer_urls = miami_mapper().get_metadata(
        key="transfer-urls",
        source_metadata=deleted_record_dict
    )

    assert result_source_organization == "https://d-nb.info/gnd/5091030-9"
    assert result_origin_system_identifier == "oai"
    assert result_external_identifier == "id0"
    assert result_transfer_urls is None
