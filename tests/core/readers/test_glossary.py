# -*- coding: utf-8 -*-
import pytest

from pyramid_oereb.core.sources import Base
from pyramid_oereb.core.readers.glossary import GlossaryReader
from pyramid_oereb.core.records.glossary import GlossaryRecord
from tests.mockrequest import MockParameter


@pytest.mark.run(order=2)
def test_init(pyramid_oereb_test_config):
    reader = GlossaryReader(
        pyramid_oereb_test_config.get_glossary_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_glossary_config().get('source').get('params')
    )
    assert isinstance(reader._source_, Base)


@pytest.mark.run(order=2)
def test_read(pyramid_oereb_test_config):
    reader = GlossaryReader(
        pyramid_oereb_test_config.get_glossary_config().get('source').get('class'),
        **pyramid_oereb_test_config.get_glossary_config().get('source').get('params')
    )
    results = reader.read(MockParameter())
    assert isinstance(results, list)
    assert isinstance(results[0], GlossaryRecord)
    assert len(results) == 1
    assert results[0].title['de'] == 'AGI'
    assert results[0].title['fr'] == 'SGRF'
    assert 'Geoinformation' in results[0].content['de']
