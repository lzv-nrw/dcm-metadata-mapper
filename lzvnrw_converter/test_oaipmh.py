"""
Test suite for the OAI-PMH-specific implementation of the source metadata
converter.
"""
import pytest
from lzvnrw_converter.oaipmh_converter import OAIPMHMetadataConverter


@pytest.fixture(name="minimal_xml")
def get_minimal_xml():
    """Returns a minimal XML for testing the OAIPMHMetadataConverter() class."""
    return \
        """<OAI-PMH>
            <responseDate>2023-09-12T06:45:12Z</responseDate>
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
                        </oai_dc:dc>
                    </metadata>
                </record>
            </GetRecord>
        </OAI-PMH>
        """

def test_basic_conversion(minimal_xml):
    """From a static input-xml, assert that the expected output is returned."""
    some_converter = OAIPMHMetadataConverter()

    result = some_converter.get_dict(minimal_xml)

    assert isinstance(result, dict)
    assert "header" in result
    