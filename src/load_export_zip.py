"""
Load an mmap (folder) and save as zip
"""
import os
from pprint import pprint

import pandas as pd

# turn off pandas SettingWithCopyWarning
pd.options.mode.copy_on_write = True

from mapmanagercore import MapAnnotations, mmMapLoader
from mapmanagercore.logger import logger

def load_map_save_zip():
    """Load mmap and save as zip.
    """
    path = 'data/202504/single_timepoint_202504.mmap'

    # uncompressed using macOS finder
    path = '/Users/cudmore/Sites/MapManagerCore-Data/data/202504/mmap_from_zip/single_timepoint_202504.mmap'

    if not os.path.isdir(path):
        logger.error(f'did not find file: {path}')
        return
    
    logger.info(f'=== loading path:{path}')
    mmap = MapAnnotations.load(path)
    print(mmap)
    
    # try to convert points to json
    # shapely columns in geodataframe can not be converted to json
    if 0:
        print(f'mmap.points:{type(mmap.points)}')  # LazyGeoFrame
        print(f'mmap.points[:]:{type(mmap.points[:])}')  # GeoDataFrame
        _points = mmap.points[:].set_geometry('point') 
        logger.info(f'after set_geometry() _points: {type(_points)}')  # GeoDataFrame
        print(_points)
        # TypeError: Object of type Point is not JSON serializable
        # logger.info('_points to_json()')
        #print(_points.to_json())  # TypeError: Object of type Point is not JSON serializable
        import geopandas as gp
        # ValueError: CRS mismatch between CRS of the passed geometries and 'crs'. Use 'GeoDataFrame.set_crs(crs, allow_override=True)' to overwrite CRS or 'GeoDataFrame.to_crs(crs)' to reproject geometries. 
        _newGeoDataFrame = gp.GeoDataFrame(_points, crs="EPSG:3857")
        logger.info(f'_newGeoDataFrame:{type(_newGeoDataFrame)}:')
        print(_newGeoDataFrame)

    return

    # logger.info('=== points[:]')
    # pprint(mmap.points[:])

    # _json = mmap.points[:].to_json(orient='index')
    # # _dict = mmap.points[:].to_dict(orient='tight')
    # logger.info(f'=== to_json')
    # pprint(_json)

    # logger.info(f'=== read_json dict')
    # _newDf = pd.read_json(_json, orient='index')
    # print(_newDf)

    # return

    # logger.info('=== columns')
    # for column in mmap.points.columns:
    #     print(f'column:{column} {type(column)}')

    # logger.info('=== attributes')
    # print(mmap.points.attributes)

    # save as zip
    zipPath = path + '.zip'
    logger.info(f'=== saving zip:{zipPath}')
    mmap.save(zipPath)

    # reload zip
    zipMap = MapAnnotations.load(zipPath)
    print(zipMap)

def tryLoadZip():
    import zarr
    
    # reload zip
    zipPath = 'data/202504/single_timepoint_202504.mmap.zip'
    mmap = MapAnnotations.load(zipPath)
    print(mmap)
    
    return

    # zip from command line, like:
    # zip -r0 single_timepoint_202504.mmap.zip single_timepoint_202504.mmap/  
    zipPath = '/Users/cudmore/Sites/MapManagerCore-Data/data/202504/single_timepoint_202504.mmap.zip'
        
    if not os.path.isfile(zipPath):
        print('error')
        return

    logger.info(f'=== reloading zip path:{zipPath}')

    # works
    import zipfile
    # with zarr.ZipStore(zipPath, mode='r', compression=zipfile.ZIP_STORED) as store:
    with zarr.ZipStore(zipPath, mode='r') as store:
        logger.info(f'store:{store}')
        # group = zarr.group(store=store)  # /
        group = zarr.open(store=store, mode='r')  # / zarr.hierarchy.Group
        print(list(group.keys()))  # '1'
        attrs:zarr.attrs.Attributes = group.attrs  # zarr.attrs.Attributes
        logger.warning(f'attrs is:{attrs}')
        #print(list(attrs.keys()))
        # _metadataDict: dict = attrs['metadata']
              
    # broken
    # mmap = MapAnnotations.load(zipPath)
    # print(mmap)
    
    # logger.info('=== columns')
    # print(mmap.points.columns)
    
    # logger.info('=== attributes')
    # print(mmap.points.attributes)

if __name__ == '__main__':
    # load_map_save_zip()  # load mmap and save as zip

    tryLoadZip()