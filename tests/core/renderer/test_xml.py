# -*- coding: utf-8 -*-

import pytest
from io import BytesIO
from lxml import etree

from pyramid_oereb.core.renderer.extract.xml_ import Renderer
from pyramid_oereb.core.renderer.versions.xml_ import Renderer as VersionsRenderer
from pyramid_oereb.core.views.webservice import Parameter
from tests.mockrequest import MockRequest


def test_get_gml_id():
    renderer = Renderer(None)
    assert renderer._get_gml_id() == 'gml1'
    assert renderer._get_gml_id() == 'gml2'
    assert renderer._get_gml_id() == 'gml3'


def test_version_against_schema(schema_xml_versions, DummyRenderInfo):
    versions = {
        u'GetVersionsResponse': {
            u'supportedVersion': [
                {
                    u'version': u'1.0',
                    u'serviceEndpointBase': u'https://example.com'
                }
            ]
        }
    }
    renderer = VersionsRenderer(DummyRenderInfo())
    rendered = renderer._render(versions)

    xmlschema_doc = etree.parse(schema_xml_versions)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    buffer = BytesIO(rendered)
    doc = etree.parse(buffer)
    assert xmlschema.validate(doc)


# #TODO: check if fixtures work in this case
@pytest.mark.parametrize('parameter, test_extract', [
    (
            Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
            'get_default_extract'
    ),
    (
            Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
            'get_empty_glossary_extract'
    ),
    (
            Parameter('reduced', 'xml', False, False, 'BL0200002829', '1000', 'CH775979211712', 'de'),
            'get_none_glossary_extract'
    )
])
def test_extract_against_schema(schema_xml_extract, DummyRenderInfo, parameter, test_extract):
    extract = test_extract
    renderer = Renderer(DummyRenderInfo())
    renderer._language = u'de'
    renderer._request = MockRequest()
    renderer._request.route_url = lambda url, **kwargs: "http://example.com/current/view"
    rendered = renderer._render(extract, parameter)

    xmlschema_doc = etree.parse(schema_xml_extract)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    buffer = BytesIO(rendered)
    doc = etree.parse(buffer)
    xmlschema.assertValid(doc)
