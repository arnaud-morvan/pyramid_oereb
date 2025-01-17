# -*- coding: utf-8 -*-
import os
import json
import codecs
import pytest
from pyramid_oereb.contrib.print_proxy.mapfish_print.mapfish_print import Renderer
from pyramid_oereb.contrib.print_proxy.mapfish_print.toc_pages import TocPages


@pytest.fixture
def coordinates():
    yield [[[
        [2615122.772, 1266688.951], [2615119.443, 1266687.783], [2615116.098, 1266686.662],
        [2615112.738, 1266685.586], [2615109.363, 1266684.556], [2615105.975, 1266683.573],
        [2615102.573, 1266682.637], [2615098.859, 1266681.622], [2615095.13, 1266680.663],
        [2615122.772, 1266688.951]
    ]]]


@pytest.fixture
def extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/test_extract.json'
    ) as f:
        yield json.load(f)


@pytest.fixture
def expected_printable_extract():
    with codecs.open(
            'tests/contrib/print_proxy/resources/expected_getspec_extract.json'
    ) as f:
        yield json.load(f)


@pytest.fixture
@pytest.mark.usefixtures('coordinates')
def geometry(coordinates):
    yield {
        'type': 'MultiPolygon',
        'coordinates': coordinates
    }


def test_toc_pages():
    assert TocPages(extract()).getNbPages() == 1


def getSameEntryInList(reference, objects):
    sameObject = None

    # List are not supported
    if isinstance(reference, list):
        for obj in objects:
            if reference == obj:
                return obj

    # Dict reference
    elif isinstance(reference, dict):
        for obj in objects:
            if isinstance(obj, dict):
                sameObject = obj
                for key in reference:
                    if key not in obj or not deepCompare(reference[key], obj[key], False):
                        sameObject = None
                        break
            if sameObject is not None:
                return sameObject

    # Naked value reference
    else:
        for obj in objects:
            if obj == reference:
                return obj

    return None


def deepCompare(value, valueToCompare, verbose=True):
    match = True
    # Go inside dict to compare values inside
    if isinstance(value, dict):
        if not isinstance(valueToCompare, dict):
            match = False
        else:
            for key in value:
                if not deepCompare(value[key], valueToCompare[key]):
                    match = False
                    break

    # Go inside list to compare values inside
    elif isinstance(value, list):
        if not isinstance(valueToCompare, list):
            match = False
        else:
            for index, element in enumerate(value):
                entry = value[index]
                # Index can change try to find the same entry
                matchEntry = getSameEntryInList(entry, valueToCompare)
                if not deepCompare(entry, matchEntry):
                    match = False
                    break

    # Compare values
    elif value != valueToCompare:
        match = False

    if not match and verbose and valueToCompare is not None:
        print(u"Error with value {} expected {}".format(value, valueToCompare))
    return match


def test_legend(extract, geometry, DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo)
    renderer.convert_to_printable_extract(extract, geometry())
    first_plr = extract.get('RealEstate_RestrictionOnLandownership')[0]
    assert isinstance(first_plr, dict)


def test_mapfish_print_entire_extract(extract, expected_printable_extract, DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    renderer.convert_to_printable_extract(extract, geometry)
    # Uncomment to print the result
    # f = open('/workspace/printable_extract.json', 'w')
    # f.write(json.dumps(printable_extract))
    # f.close()

    assert deepCompare(extract, expected_printable_extract)
    # Do it twice, to test all keys in each reports
    assert deepCompare(expected_printable_extract, extract)


def test_get_sorted_legend(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_legend_list = [
        {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 11432,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 164,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, überwachungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp1',
            'Geom_Type': u'NrOfPoints',
            'TypeCodelist': '',
            'NrOfPoints': 2,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp1',
            'LegendText': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 2000,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 114,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }
    ]
    sorted_list = renderer.sort_dict_list(test_legend_list, renderer.sort_legend_elem)
    expected_result = [
        {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 11432,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp2',
            'Geom_Type': u'AreaShare',
            'TypeCodelist': '',
            'AreaShare': 114,
            'PartInPercent': 32.6,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp2',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 2000,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, untersuchungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp3',
            'Geom_Type': u'LengthShare',
            'TypeCodelist': '',
            'LengthShare': 164,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp3',
            'LegendText': u'Belastet, überwachungsbedürftig'
        }, {
            'TypeCode': u'StaoTyp1',
            'Geom_Type': u'NrOfPoints',
            'TypeCodelist': '',
            'NrOfPoints': 2,
            'SymbolRef': u'http://localhost:6543/oereb/image/symbol/\
                        ch.BelasteteStandorteOeffentlicherVerkehr/1/StaoTyp1',
            'LegendText': u'Belastet, keine schädlichen oder lästigen Einwirkungen zu erwarten'
        }
    ]
    assert sorted_list == expected_result


def test_get_sorted_legal_provisions(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    expected_result = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }
    ]
    test_legal_provisions = [
        {
           "Canton": "BL",
           "DocumentType": "LegalProvision",
           "Lawstatus_Code": "inKraft",
           "Lawstatus_Text": "Rechtskräftig",
           "OfficialNumber": "07.447",
           "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
           "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
           "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
           "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }
    ]
    assert expected_result == renderer.sort_dict_list(test_legal_provisions, renderer.sort_legal_provision)


def test_get_sorted_hints(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_hints = [{
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
        "Title": "Revision Ortsplanung"
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 1,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 2,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
        "Title": "Baugesetz"

    }]

    expected_result = [{
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 1,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "index": 2,
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
        "Title": "Baugesetz"
    }, {
        "Canton": "BL",
        "DocumentType": "Hint",
        "Lawstatus_Code": "inKraft",
        "Lawstatus_Text": "Rechtskräftig",
        "OfficialNumber": "3891.100",
        "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
        "ResponsibleOffice_OfficeAtWeb": "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
        "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
        "Title": "Revision Ortsplanung"
    }]

    assert expected_result == renderer.sort_dict_list(test_hints, renderer.sort_hints_laws)


def test_get_sorted_law(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_law = [
        {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': 'http://www.admin.ch/ch/d/sr/c814_01.html'}],
            'Title': 'Raumplanungsverordnung für den Kanton Graubünden',
            'Abbreviation': 'KRVO',
            'OfficialNumber': 'BR 801.110',
            'index': 5,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2934?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'index': 3,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden2',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 1,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': 'Bundesgesetz über die Raumplanung',
            'Abbreviation': 'RPG',
            'OfficialNumber': 'SR 700',
            'index': 4,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': 'http://www.lexfind.ch/dtah/167348/2'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 2,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }
    ]

    expected_result = [
        {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden2',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 1,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'OfficialNumber': u'BR 801.100',
            'index': 2,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': u'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': u'Raumplanungsgesetz für den Kanton Graubünden',
            'Abbreviation': u'KRG',
            'index': 3,
            'Canton': u'GR',
            'Lawstatus_Code': u'inKraft',
            'Lawstatus_Text': u'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                u'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2936?locale=de'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': u'http://www.admin.ch/ch/d/sr/c814_680.html'}],
            'Title': 'Bundesgesetz über die Raumplanung',
            'Abbreviation': 'RPG',
            'OfficialNumber': 'SR 700',
            'index': 4,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb': 'http://www.lexfind.ch/dtah/167348/2'
        }, {
            'DocumentType': 'Law',
            'TextAtWeb': [{'URL': 'http://www.admin.ch/ch/d/sr/c814_01.html'}],
            'Title': 'Raumplanungsverordnung für den Kanton Graubünden',
            'Abbreviation': 'KRVO',
            'OfficialNumber': 'BR 801.110',
            'index': 5,
            'Canton': 'GR',
            'Lawstatus_Code': 'inKraft',
            'Lawstatus_Text': 'Rechtskräftig',
            'ResponsibleOffice_Name': u'Bundesamt für Verkehr BAV',
            'ResponsibleOffice_OfficeAtWeb':
                'https://www.gr-lex.gr.ch/frontend/versions/pdf_file_with_annex/2934?locale=de'
        }
    ]
    assert expected_result == renderer.sort_dict_list(test_law, renderer.sort_hints_laws)


def test_group_legal_provisions(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    test_legal_provisions = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"}],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"}],
            "Title": "Revision Ortsplanung"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [{"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"}],
            "Title": "Revision Ortsplanung"
        }
    ]
    expected_results = [
        {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "3891.100",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/197"},
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/198"},
            ],
            "Title": "Baugesetz"
        }, {
            "Canton": "BL",
            "DocumentType": "LegalProvision",
            "Lawstatus_Code": "inKraft",
            "Lawstatus_Text": "Rechtskräftig",
            "OfficialNumber": "07.447",
            "ResponsibleOffice_Name": "Bundesamt für Verkehr BAV",
            "ResponsibleOffice_OfficeAtWeb":
                "http://www.bav.admin.ch/themen/verkehrspolitik/00709/index.html",
            "TextAtWeb": [
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/213"},
                {"URL": "https://oereb-gr-preview.000.ch/api/attachments/214"},
            ],
            "Title": "Revision Ortsplanung"
        }
    ]

    assert expected_results == renderer.group_legal_provisions(test_legal_provisions)


def test_archive_pdf(DummyRenderInfo):
    renderer = Renderer(DummyRenderInfo())
    extract = {'RealEstate_EGRID': 'CH113928077734'}
    path_and_filename = renderer.archive_pdf_file('/tmp', bytes(), extract)
    assert os.path.isfile(path_and_filename)
