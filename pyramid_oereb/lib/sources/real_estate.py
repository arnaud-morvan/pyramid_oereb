# -*- coding: utf-8 -*-
from geoalchemy2.elements import _SpatialElement
from sqlalchemy.orm.exc import NoResultFound

from pyramid_oereb.lib.sources import BaseDatabaseSource, Base
from pyramid_oereb.lib.records.real_estate import RealEstateRecord
from geoalchemy2.shape import to_shape


class RealEstateBaseSource(Base):
    _record_class_ = RealEstateRecord

    def read(self, nb_ident=None, number=None, egrid=None, geometry=None):
        pass


class RealEstateDatabaseSource(BaseDatabaseSource, RealEstateBaseSource):

    def read(self, nb_ident=None, number=None, egrid=None, geometry=None):
        """
        Central method to read all plrs (geometry input) or explicitly one plr (nb_ident+number/egrid input).
        :param nb_ident: The identification number of the desired real estate. This parameter is directly
        related to the number parameter and both must be set! Combination will deliver only one result or
        crashes.
        :type nb_ident: int or None
        :param number: The number of parcel or also known real estate. This parameter is directly
        related to the nb_ident parameter and both must be set! Combination will deliver only one result or
        crashes.
        :type number: str or None
        :param egrid: The unique identifier of the desired real estate. This will deliver only one result or
        crashes.
        :type: str or None
        :param geometry: A geometry as WKT string which is used to obtain intersected real estates. This may
        deliver several results.
        :type geometry: str
        """
        try:
            session = self._adapter_.get_session(self._key_)
            query = session.query(self._model_)
            if nb_ident and number:
                # explicitly querying for one result, this will cause an error if more than one ore none
                results = [
                    query.filter(self._model_.number == number).filter(self._model_.identdn == nb_ident).one()
                ]
            elif egrid:
                # explicitly querying for one result, this will cause an error if more than one ore none
                results = [
                    query.filter(self._model_.egrid == egrid).one()
                ]
            elif geometry:
                # querying for all results
                results = query.filter(self._model_.limit.ST_Intersects(geometry)).all()
            else:
                raise AttributeError('Necessary parameter were missing.')

            self.records = list()
            for result in results:
                self.records.append(self._record_class_(
                    result.type,
                    result.canton,
                    result.municipality,
                    result.fosnr,
                    result.land_registry_area,
                    to_shape(result.limit) if isinstance(result.limit, _SpatialElement) else None,
                    result.metadata_of_geographical_base_data,
                    number=result.number,
                    identdn=result.identdn,
                    egrid=result.egrid
                ))
        except NoResultFound, e:
            raise LookupError(e)
