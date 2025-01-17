# -*- coding: utf-8 -*-
"""
This is a full representation of the data model defined by the federal definition.

**It is representing the topic: ${topic}**

You can use it to
produce a own new topic for the oereb eco system in the specifications shape. To be able to adapt this
models to your own infrastructure you must implement the same attribute names! In fact that inheritance
is not easily made you need to make your own classes and adapt them to your database.
"""
import sqlalchemy as sa
from pyramid_oereb.standard.models import NAMING_CONVENTION
from pyramid_oereb.lib.config import Config
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.types import Geometry as GeoAlchemyGeometry
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base()
srid = Config.get('srid')


class Availability(Base):
    """
    A simple bucket for achieving a switch per municipality. Here you can configure via the imported data if
    a public law restriction is available or not. You need to fill it with the data you provided in the
    app schemas municipality table (fosnr).

    Attributes:
        fosnr (int): The identifier of the municipality in your system (id_bfs = fosnr)
        available (bool): The switch field to configure if this plr is available for the
            municipality or not.  This field has direct influence on the applications
            behaviour. See documentation for more info.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'availability'
    fosnr = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    available = sa.Column(sa.Boolean, nullable=False, default=False)


class Office(Base):
    """
    The bucket to fill in all the offices you need to reference from public law restriction, document,
    geometry.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        name (dict): The multilingual name of the office.
        office_at_web (dict): A web accessible url to a presentation of this office (multilingual).
        uid (str): The uid of this office from https
        line1 (str): The first address line for this office.
        line2 (str): The second address line for this office.
        street (str): The streets name of the offices address.
        number (str): The number on street.
        postal_code (int): The ZIP-code.
        city (str): The name of the city.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'office'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    name = sa.Column(JSONType, nullable=False)
    office_at_web = sa.Column(JSONType, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)
    line1 = sa.Column(sa.String, nullable=True)
    line2 = sa.Column(sa.String, nullable=True)
    street = sa.Column(sa.String, nullable=True)
    number = sa.Column(sa.String, nullable=True)
    postal_code = sa.Column(sa.Integer, nullable=True)
    city = sa.Column(sa.String, nullable=True)


class DataIntegration(Base):
    """
    The bucket to fill in the date when this whole schema was updated. It has a relation to the office to be
    able to find out who was the delivering instance.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        date (datetime.date): The date when this data set was delivered.
        office_id (int): A foreign key which points to the actual office instance.
        office (pyramid_oereb.standard.models.${schema_name}.Office):
            The actual office instance which the id points to.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'data_integration'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    date = sa.Column(sa.DateTime, nullable=False)
    office_id = sa.Column(sa.Integer, sa.ForeignKey(Office.id), nullable=False)
    office = relationship(Office)
    checksum = sa.Column(sa.String, nullable=True)


class Document(Base):
    """
    THE DOCUMENT
    This represents the main document in the whole system.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        document_type (str): The document type. It must be "Rechtsvorschrift", "GesetzlicheGrundlage"
            or "Hinweis".
        index (int): An index used to sort the documents.
        law_status (str): The status switch if the document is legally approved or not.
        title (dict): The multilingual title or if existing the short title ot his document.
        office_id (str): The foreign key to the office which is in charge for this document.
        responsible_office (pyramid_oereb.standard.models.railways_project_planning_zones.Office):
            The dedicated relation to the office instance from database.
        published_from (datetime.date): The date from when the document should be available for
            publishing in extracts. This  directly affects the behaviour of extract
            generation.
        published_until (datetime.date): The date until when the document should be available for
            publishing on extracts. This  directly affects the behaviour of extract
            generation.
        text_at_web (dict): A multilingual link which leads to the documents content in the web.
        abbreviation (dict): The multilingual shortened version of the documents title.
        official_number (dict): The multilingual official number which uniquely identifies this document.
        only_in_municipality (int): The fosnr (=id bfs) of the municipality. If this is None it is assumed
            the document is  related to the whole canton or even the confederation.
        file (str): The document itself as a binary representation (PDF). It is string but
            BaseCode64 encoded.

    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'document'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    document_type = sa.Column(sa.String, nullable=False)
    index = sa.Column(sa.Integer, nullable=False)
    law_status = sa.Column(sa.String, nullable=False)
    title = sa.Column(JSONType, nullable=False)
    office_id = sa.Column(
        sa.String,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)
    published_from = sa.Column(sa.Date, nullable=False)
    published_until = sa.Column(sa.Date, nullable=True)
    text_at_web = sa.Column(JSONType, nullable=True)
    abbreviation = sa.Column(JSONType, nullable=True)
    official_number = sa.Column(JSONType, nullable=True)
    only_in_municipality = sa.Column(sa.Integer, nullable=True)
    file = sa.Column(sa.String, nullable=True)


class ViewService(Base):
    """
    A view service aka WM(T)S which can deliver a cartographic representation via web.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        reference_wms (dict): The actual url which leads to the desired cartographic representation
            (multilingual)
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'view_service'
    id = sa.Column(sa.String, primary_key=True, autoincrement=False)
    reference_wms = sa.Column(JSONType, nullable=False)


class LegendEntry(Base):
    """
    A class based legend system which is directly related to
    :class:`pyramid_oereb.standard.models.${schema_name}.ViewService`.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        symbol (str): An image with represents the legend entry. This can be png or svg. It is string
            but BaseCode64  encoded.
        legend_text (dict): Multilingual text to describe this legend entry.
        type_code (str): Type code of the public law restriction which is represented by this legend
            entry.
        type_code_list (str): List of all public law restrictions which are described through this
            legend  entry.
        topic (str): Statement to describe to which public law restriction this legend entry
            belongs.
        sub_theme (dict): Multilingual description for sub topics this legend entry might belonging to.
        view_service_id (int): The foreign key to the view service this legend entry is related to.
        view_service (pyramid_oereb.standard.models.${schema_name}.ViewService):
            The dedicated relation to the view service instance from database.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'legend_entry'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    symbol = sa.Column(sa.String, nullable=False)
    legend_text = sa.Column(JSONType, nullable=False)
    type_code = sa.Column(sa.String(40), nullable=False)
    type_code_list = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    sub_theme = sa.Column(sa.String, nullable=True)
    view_service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ViewService.id),
        nullable=False
    )
    view_service = relationship(ViewService, backref='legends')


class PublicLawRestriction(Base):
    """
    The container where you can fill in all your public law restrictions to the topic.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        legend_text (dict): The multilingual textual representation of the public law restriction.
        topic (str): Category for this public law restriction (name of the topic).
        sub_theme (str): Multilingual textual explanation to subtype the topic attribute.
        type_code (str): Type code of the public law restriction machine readable based on the
            original data  model of this public law restriction.
        type_code_list (str): List of full range of type_codes for this public law restriction in a
            machine  readable format.
        law_status (str): The status switch if the document is legally approved or not.
        published_from (datetime.date): The date when the document should be available for
            publishing on extracts. This  directly affects the behaviour of extract
            generation.
        view_service_id (int): The foreign key to the view service this public law restriction is
            related to.
        view_service (pyramid_oereb.standard.models.${schema_name}.ViewService):
            The dedicated relation to the view service instance from database.
        office_id (int): The foreign key to the office which is responsible to this public law
            restriction.
        responsible_office (pyramid_oereb.standard.models.${schema_name}.Office):
            The dedicated relation to the office instance from database.
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'public_law_restriction'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    legend_text = sa.Column(JSONType, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    sub_theme = sa.Column(sa.String, nullable=True)
    type_code = sa.Column(sa.String(40), nullable=True)
    type_code_list = sa.Column(sa.String, nullable=True)
    law_status = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    view_service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ViewService.id),
        nullable=False
    )
    view_service = relationship(
        ViewService,
        backref='public_law_restrictions'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class Geometry(Base):
    """
    The dedicated model for all geometries in relation to their public law restriction.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        law_status (str): The status switch if the document is legally approved or not.
        published_from (datetime.date): The date when the document should be available for
            publishing on extracts. This  directly affects the behaviour of extract
            generation.
        geo_metadata (str): A link to the metadata which this geometry is based on which delivers
            machine  readable response format (XML).
        public_law_restriction_id (int): The foreign key to the public law restriction this geometry
            is  related to.
        public_law_restriction (pyramid_oereb.standard.models.${schema_name}
            .PublicLawRestriction): The dedicated relation to the public law restriction instance from
            database.
        office_id (int): The foreign key to the office which is responsible to this public law
            restriction.
        responsible_office (pyramid_oereb.standard.models.${schema_name}.Office):
            The dedicated relation to the office instance from database.
        geom (geoalchemy2.types.Geometry): The geometry it's self. For type information see
            geoalchemy docs (https://geoalchemy-2.readthedocs.io/en/0.4.2/types.html) dependent on the
            configured type.  This concrete one is ${geometry_type}
    """
    __table_args__ = {'schema': '${schema_name}'}
    __tablename__ = 'geometry'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    law_status = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    geo_metadata = sa.Column(sa.String, nullable=True)
    geom = sa.Column(GeoAlchemyGeometry('${geometry_type}', srid=srid), nullable=False)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction = relationship(
        PublicLawRestriction,
        backref='geometries'
    )
    office_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Office.id),
        nullable=False
    )
    responsible_office = relationship(Office)


class PublicLawRestrictionBase(Base):
    """
    Meta bucket (join table) for public law restrictions which acts as a base for other public law
    restrictions.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        public_law_restriction_id (int): The foreign key to the public law restriction which bases
            on another  public law restriction.
        public_law_restriction_base_id (int): The foreign key to the public law restriction which is
            the  base for the public law restriction.
        plr (pyramid_oereb.standard.models.${schema_name}.PublicLawRestriction):
            The dedicated relation to the public law restriction (which bases on) instance from  database.
        base (pyramid_oereb.standard.models.${schema_name}.PublicLawRestriction):
            The dedicated relation to the public law restriction (which is the base) instance from database.
    """
    __tablename__ = 'public_law_restriction_base'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_base_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        PublicLawRestriction,
        backref='basis',
        foreign_keys=[public_law_restriction_id]
    )
    base = relationship(
        PublicLawRestriction,
        foreign_keys=[public_law_restriction_base_id]
    )


class PublicLawRestrictionRefinement(Base):
    """
    Meta bucket (join table) for public law restrictions which acts as a refinement for other public law
    restrictions.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        public_law_restriction_id (int): The foreign key to the public law restriction which is
            refined by  another public law restriction.
        public_law_restriction_refinement_id (int): The foreign key to the public law restriction
            which is  the refinement of the public law restriction.
        plr (pyramid_oereb.standard.models.${schema_name}.PublicLawRestriction):
            The dedicated relation to the public law restriction (which refines) instance from  database.
        base (pyramid_oereb.standard.models.${schema_name}.PublicLawRestriction):
            The dedicated relation to the public law restriction (which is refined) instance from database.
    """
    __tablename__ = 'public_law_restriction_refinement'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    public_law_restriction_refinement_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    plr = relationship(
        PublicLawRestriction,
        backref='refinements',
        foreign_keys=[public_law_restriction_id]
    )
    refinement = relationship(
        PublicLawRestriction,
        foreign_keys=[public_law_restriction_refinement_id]
    )


class PublicLawRestrictionDocument(Base):
    """
    Meta bucket (join table) for the relationship between public law restrictions and documents.

    Attributes:
        id (int): The identifier. This is used in the database only and must not be set manually. If
            you  don't like it - don't care about.
        public_law_restriction_id (int): The foreign key to the public law restriction which has
            relation to  a document.
        document_id (int): The foreign key to the document which has relation to the public law
            restriction.
        plr (pyramid_oereb.standard.models.${schema_name}.PublicLawRestriction):
            The dedicated relation to the public law restriction instance from database.
        document (pyramid_oereb.standard.models.${schema_name}.Document):
            The dedicated relation to the document instance from database.
    """
    __tablename__ = 'public_law_restriction_document'
    __table_args__ = {'schema': '${schema_name}'}
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    public_law_restriction_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(PublicLawRestriction.id),
        nullable=False
    )
    document_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Document.id),
        nullable=False
    )
    plr = relationship(
        PublicLawRestriction,
        backref='legal_provisions'
    )
    document = relationship(
        Document
    )
    article_numbers = sa.Column(sa.String, nullable=True)
