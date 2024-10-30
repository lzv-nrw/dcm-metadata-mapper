"""
Test suite for the hfm-OPUS-specific implementation
of the source metadata mapper.
"""
import pytest
from lzvnrw_converter.oaipmh_converter import OAIPMHMetadataConverter
from lzvnrw_mapper.hfm_opus import HfmOpusMetadataMapper


@pytest.fixture(name="minimal_source_dict_hfm_opus")
def get_minimal_source_dict_hfm_opus():
    """
    Returns a dict from a given minimal XML for testing the hfm-opus mapper.
    """
    some_converter = OAIPMHMetadataConverter()

    return some_converter.get_dict(
"""<OAI-PMH>
    <responseDate>2023-09-12T06:45:12Z</responseDate>
    <request>https://opus.hfm-detmold.de/oai</request>
    <GetRecord>
        <record>
            <header>
                <identifier>oai:opus.hfm-detmold.de:x</identifier>
            </header>
            <metadata>
                <oai_dc:dc>
                    <dc:creator>Mustermann, M.</dc:creator>
                    <dc:creator>Mustermann, E.</dc:creator>
                    <dc:title xml:lang="de">This is a test</dc:title>
                    <dc:identifier>
                        https://nbn-resolving.org/urn:nbn:de:hbz:x-xxxxxxxxxxx
                    </dc:identifier>
                    <dc:identifier>urn:nbn:de:hbz:x-xxxxxxxxxxx</dc:identifier>
                    <dc:identifier>
                        https://opus.hfm-detmold.de/files/xx/xxxxxxxxxxx.pdf
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


@pytest.fixture(name="hfm_opus_mapper")
def get_hfm_opus_mapper():
    """Returns a hfm_opus mapper."""
    return HfmOpusMetadataMapper


def test_hfm_opus_map(
    minimal_source_dict_hfm_opus,
    hfm_opus_mapper
):
    """
    Test the hfm_opus mapper.
    From an input dict, assert that the expected outputs are returned.
    """

    assert hfm_opus_mapper().MAPPER_TAG == "Hfm OPUS Metadata Mapper"

    # DC-Creator
    result_dc_creator = hfm_opus_mapper().get_metadata(
        key="DC-Creator",
        source_metadata=minimal_source_dict_hfm_opus
    )
    assert isinstance(result_dc_creator, list)
    assert len(result_dc_creator) == 2
    assert result_dc_creator[0] == "Mustermann, M."
    assert result_dc_creator[1] == "Mustermann, E."

    # DC-Title
    result_dc_title = hfm_opus_mapper().get_metadata(
        key="DC-Title",
        source_metadata=minimal_source_dict_hfm_opus
    )
    assert result_dc_title == "This is a test"

    # DC-Terms-Identifier
    result_dc_terms_id = hfm_opus_mapper().get_metadata(
        "DC-Terms-Identifier",
        minimal_source_dict_hfm_opus
    )
    assert len(result_dc_terms_id) == 2

    # Origin-System-Identifier
    result_origin_system_identifier = \
        hfm_opus_mapper().get_metadata(
            "Origin-System-Identifier",
            minimal_source_dict_hfm_opus
        )
    assert result_origin_system_identifier == "oai:opus.hfm-detmold.de"

    # External-Identifier
    result_external_identifier = \
        hfm_opus_mapper().get_metadata(
            "External-Identifier",
            minimal_source_dict_hfm_opus
        )
    assert result_external_identifier \
        == "x"

    # Source-Organization
    result_source_organization = \
        hfm_opus_mapper().get_metadata(
            "Source-Organization",
            minimal_source_dict_hfm_opus
        )
    assert result_source_organization == "https://d-nb.info/gnd/5073685-1"

    # transfer-urls
    result_transfer_urls = \
        hfm_opus_mapper().get_metadata(
            "transfer-urls",
            minimal_source_dict_hfm_opus
        )
    assert result_transfer_urls ==\
        ["https://opus.hfm-detmold.de/files/xx/xxxxxxxxxxx.pdf"]


def test_get_specversion(hfm_opus_mapper):
    """
    Test the public get-method for _SPECVERSION.
    """
    mapper_specversion = hfm_opus_mapper().get_specversion()
    assert all(isinstance(n, int) for n in mapper_specversion[0:3])
    assert isinstance(mapper_specversion[3], str)


def test_deleted_record(deleted_record_dict, hfm_opus_mapper):
    """
    Ensure the deleted record is mapped as expected without errors.
    """

    result_source_organization = hfm_opus_mapper().get_metadata(
        key="source-organization",
        source_metadata=deleted_record_dict
    )
    result_origin_system_identifier = hfm_opus_mapper().get_metadata(
        key="origin-system-identifier",
        source_metadata=deleted_record_dict
    )
    result_external_identifier = hfm_opus_mapper().get_metadata(
        key="external-identifier",
        source_metadata=deleted_record_dict
    )
    result_transfer_urls = hfm_opus_mapper().get_metadata(
        key="transfer-urls",
        source_metadata=deleted_record_dict
    )

    assert result_source_organization == "https://d-nb.info/gnd/5073685-1"
    assert result_origin_system_identifier == "oai"
    assert result_external_identifier == "id0"
    assert result_transfer_urls is None