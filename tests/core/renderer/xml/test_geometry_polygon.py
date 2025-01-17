# -*- coding: utf-8 -*-

import pytest
from tests.core.renderer.xml import params
from shapely.geometry import Polygon


@pytest.mark.parametrize('parameters', params)  # noqa
def test_polygon(template, parameters):
    polygon = Polygon(
        ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)),
        [((0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25), (0.25, 0.25))]
    )

    def get_gml_id():
        return 'gml1'

    content = template.render(**{
        'params': parameters,
        'default_language': 'de',
        'polygon': polygon,
        'get_gml_id': get_gml_id
    }).decode('utf-8').split('\n')
    expected_content = """

    <gml:Polygon gml:id="gml1">
        <gml:exterior>
            <gml:LinearRing>
                <gml:posList>
                    0.0 0.0 0.0 1.0 1.0 1.0 1.0 0.0 0.0 0.0
                </gml:posList>
            </gml:LinearRing>
        </gml:exterior>
        <gml:interior>
            <gml:LinearRing>
                <gml:posList>
                    0.25 0.25 0.25 0.75 0.75 0.75 0.75 0.25 0.25 0.25
                </gml:posList>
            </gml:LinearRing>
        </gml:interior>
    </gml:Polygon>
    """.split('\n')
    expected_lines = []
    for line in expected_content:
        expected_lines.append(line.strip())
    content_lines = []
    for line in content:
        content_lines.append(line.strip())
    assert expected_lines == content_lines
