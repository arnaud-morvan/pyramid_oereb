# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.sources import BaseDatabaseSource
from pyramid_oereb.lib.sources.address import AddressBaseSource


class DatabaseSource(BaseDatabaseSource, AddressBaseSource):

    def read(self, street_name, zip_code, street_number):
        """
        Central method to read one address.

        Args:
            street_name (unicode): The name of the street for the desired address.
            zip_code (int): The postal zipcode for the desired address.
            street_number (str): The house or so called street number of the desired address.
        """
        session = self._adapter_.get_session(self._key_)
        try:
            query = session.query(self._model_)
            results = [query.filter(
                self._model_.street_name == street_name
            ).filter(
                self._model_.zip_code == zip_code
            ).filter(
                self._model_.street_number == street_number
            ).one()]

            self.records = []
            for result in results:
                self.records.append(self._record_class_(
                    result.street_name,
                    result.zip_code,
                    result.street_number,
                    to_shape(result.geom).wkt if isinstance(result.geom, _SpatialElement) else None
                ))

        except NoResultFound:
            self.records = []

        finally:
            session.close()
