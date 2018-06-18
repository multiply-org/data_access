"""
Description
===========

This module contains MULTIPLY Data Set Meta Info Providers. The purpose of these is to extract meta data information
from an existing file.
"""

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from abc import ABCMeta, abstractmethod
from multiply_data_access.data_access import DataSetMetaInfo
import gdal
import osr
import xml.etree.ElementTree as ET

class DataSetMetaInfoProvider(metaclass=ABCMeta):

    @classmethod
    def name(cls) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        """Whether the data at the given path is a valid data product for the type."""


class AWS_S2_Meta_Info_Provider(DataSetMetaInfoProvider):

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L1C'

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        #gdal_file = gdal.Open(path + '/B05.jp2')
        #projection = gdal_file.GetProjection()
        #print(projection)
        #spatial_reference = osr.SpatialReference(wkt=projection)
        self._extract_coverage_from_metadata_file()
        return DataSetMetaInfo('', '', '', '', '')

    def _get_xml_root(self, xml_file_name: str):
        tree = ET.parse(xml_file_name)
        return tree.getroot()

    def _extract_time_from_metadata_file(self, filename: str) -> str:
        """Parses the XML metadata file to extract the sensing time."""
        root = self._get_xml_root(filename + '/metadata.xml')
        for child in root:
            for x in child.findall("SENSING_TIME"):
                return x.text

    def _extract_coverage_from_metadata_file(self, filename: str) -> str:
        """Parses the XML metadata file to extract the sensing time."""
        root = self._get_xml_root(filename + '/metadata.xml')
        for child in root:
            for x in child.findall("HORIZONTAL_CS_CODE"):
                epsg_code = x.text
            for y in child.findall('Geoposition'):
                if y.tag == 'ULX':
                    ulx = int(y.text)
                if y.tag == 'ULY':
                    uly = int(y.text)
                if y.tag == 'XDIM':
                    xdim = int(y.text)
                if y.tag == 'YDIM':
                    ydim = int(y.text)
                break
        # lrx = ulx + xdim *

        for child in root:
            for x in child.findall("Tile_Angles"):
                for y in x.find("Mean_Sun_Angle"):
                    if y.tag == "ZENITH_ANGLE":
                        sza = float(y.text)
