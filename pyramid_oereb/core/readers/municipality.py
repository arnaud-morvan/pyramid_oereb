# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class MunicipalityReader(object):
    """
    The central reader for municipalities. It is directly bound to a so called source
    which is defined by a pythonic dotted string to the class definition of this source.
    An instance of the passed source will be created on instantiation of this reader class by passing through
    the parameter kwargs.
    """

    def __init__(self, dotted_source_class_path, **params):
        """
        Args:
            dotted_source_class_path
                (str or pyramid_oereb.core.sources.municipality.MunicipalityBaseSource): The
                path to the class which represents the source used by this reader. This class
                must implement basic source behaviour of the
                :ref:`api-pyramid_oereb-core-sources-municipality-municipalitybasesource`.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted name defined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self, params, fosnr=None):
        """
        The central read accessor method to get all desired records from configured source.

        .. note:: If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a list of
            :ref:`api-pyramid_oereb-core-records-municipality-municipalityrecord`. Otherwise the API like way
            the server works would be broken.

        Args:
            params (pyramid_oereb.views.webservice.Parameter): The parameters of the extract request.
            fosnr (int or None): The federal number of the municipality defined by the statistics office.

        Returns:
            pyramid_oereb.lib.records.municipality.MunicipalityRecord:
            The list of all found records. Since these are not filtered by any criteria the list simply
            contains all records delivered by the source.
        """
        self._source_.read(params, fosnr)
        return self._source_.records
