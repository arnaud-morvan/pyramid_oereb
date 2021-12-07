# -*- coding: utf-8 -*-
import pytest

from datetime import date, timedelta

from pyramid_oereb.core import b64
from pyramid_oereb.core.adapter import FileAdapter
from pyramid_oereb.contrib.data_sources.standard.sources.plr import StandardThemeConfigParser


file_adapter = FileAdapter()


@pytest.fixture
def wms_url_contaminated_sites():
    return {
        "de": "https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=default&CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740&HEIGHT=500&FORMAT=image/png&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb",
        "fr": "https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&STYLES=default&CRS=EPSG:2056&BBOX=2475000,1065000,2850000,1300000&WIDTH=740&HEIGHT=500&FORMAT=image/png&LAYERS=ch.bav.kataster-belasteter-standorte-oev.oereb",
        }

@pytest.fixture(scope='function')
def test_data_contaminated_sites(pyramid_oereb_test_config, dbsession, transact, wms_url_contaminated_sites):
    del transact
    theme_config = pyramid_oereb_test_config.get_theme_config_by_code('ch.BelasteteStandorte')
    config_parser = StandardThemeConfigParser(**theme_config)
    models = config_parser.get_models()

    view_services = {
        'view_service1': models.ViewService(
            id=1,
            reference_wms=wms_url_contaminated_sites,
            layer_index=1,
            layer_opacity=.75,
        )
        }
    dbsession.add_all(view_services.values())

    offices = {
        'office1': models.Office(
            id=1,
            name='Test office',
        )
        }
    dbsession.add_all(offices.values())

    legend_entries = {
        'legend_entry1': models.LegendEntry(
            id=1,
            symbol=b64.encode(file_adapter.read('tests/resources/symbol.png')),
            legend_text='Test',
            type_code='StaoTyp1',
            type_code_list='https://models.geo.admin.ch/BAFU/KbS_Codetexte_V1_4.xml',
            theme='ch.BelasteteStandorte',
            view_service_id=1,
        )
        }
    dbsession.add_all(legend_entries.values())

    plrs = {
        'plr1': models.PublicLawRestriction(
            id=1,
            law_status='inKraft',
            published_from=date.today().isoformat(),
            published_until=(date.today() + timedelta(days=100)).isoformat(),
            view_service_id=1,
            legend_entry_id=1,
            office_id=1,
        )
        }
    dbsession.add_all(plrs.values())

    geometries = {
        'geometry1': models.Geometry(
            id='1',
            law_status='inForce',
            published_from=date.today().isoformat(),
            published_until=(date.today() + timedelta(days=100)).isoformat(),
            geo_metadata='',
            public_law_restriction_id='1',
            geom='SRID=2056;GEOMETRYCOLLECTION(POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0)))',
        )
        }
    dbsession.add_all(geometries.values())
    dbsession.flush()
