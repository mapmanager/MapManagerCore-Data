import os
import sys

# import numpy as np
import pandas as pd  # to load igor csv files
pd.options.mode.copy_on_write = True

from mapmanagercore import MapAnnotations  #, MultiImageLoader
from mapmanagercore.logger import logger

"""Create a muli-timepoint map with images
 - progressively add segments and then segment points
    - 20240728 -->> error on adding segment point to timepoint 1

 - once we add segment, add spines to each segment

"""

localFolder = '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/'

def fetchLocalFiles(numTimepoints = 5):
    ret = {}
    
    for tp in range(numTimepoints):
        ch1 = os.path.join(localFolder, f'rr30a_s{tp}_ch1.tif')
        ch2 = os.path.join(localFolder, f'rr30a_s{tp}_ch2.tif')
        # f'/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s{tp}_ch1.tif'
        # ch2 = f'/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s{tp}_ch2.tif'

        # segmentCsv = '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s0/rr30a_s0_la.txt',

def creatZarrLoader(numTimepoints:int):
    from mapmanagercore.lazy_geo_pd_images.loader.mm_map_loader import mmMapLoader
    from mapmanagercore.data import getTiffChannel_1, getTiffChannel_2

    logger.info(f' creating empty loader')
    zl = mmMapLoader()

    path1 = getTiffChannel_1()
    path2 = getTiffChannel_2()
    
    # append a new timepoint with image data from a file
    _newTimepoint = zl.importTimepoint(path1)
    # assert ok is True
    assert zl.numTimepoints == 1

    # append another channel
    ok = zl.importChannel(path2, timepoint=_newTimepoint)
    # assert ok is True, f'importChannel tp:{tp} failed'
    assert zl.numChannels(_newTimepoint) == 2

    # from pprint import pprint
    # pprint(zl.metadata)
    logger.info(f'done num timepoints {zl.numTimepoints} numchannels = {zl.numChannels(_newTimepoint)}')
    return zl

def createMap(numTimepoints) -> MapAnnotations:
    """Create a map with a number of timepoints (images only.
    """

    # v1
    # loader = MultiImageLoader()

    # for tp in range(numTimepoints):
    #     ch1 = f'/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s{tp}_ch1.tif'
    #     ch2 = f'/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s{tp}_ch2.tif'
    #     loader.read(ch1, channel=0, time=tp)
    #     loader.read(ch2, channel=1, time=tp)

    # v2
    loader = creatZarrLoader(numTimepoints)

    # Create the annotation map
    map = MapAnnotations(loader,
                        #  lineSegments=gp.GeoDataFrame(),
                        #  points = gp.GeoDataFrame())
                         lineSegments=pd.DataFrame(),
                         points = pd.DataFrame())
    
    map.points[:]
    map.segments[:]

    # map.close()  # is this neccessary ??? Seems to close the images ???

    logger.info(f'map:{map}')
        
    return map

def loadSegments(map):
    """Load segments from our original MapManager-Igor txt files.
        Add Every 4th segment point
    
        Add all spines to each segment
    """
    # logger.info(f'1) start map:{map}')

    segmentCsvList = [
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s0/rr30a_s0_la.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s1/rr30a_s1_la.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s2/rr30a_s2_la.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s3/rr30a_s3_la.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s4/rr30a_s4_la.txt',
        ]

    spineCsvList = [
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s0/rr30a_s0_pa.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s1/rr30a_s1_pa.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s2/rr30a_s2_pa.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s3/rr30a_s3_pa.txt',
        '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s4/rr30a_s4_pa.txt',
        ]

    addEveryPoint = 4  # only add every 4 points

    _debugTpIdx = None  # 2

    # numTimepoints = map.getNumTimepoints()
    # numPntsAdded = 0  # number of tracing points
    timepointList = map.loader.metadata.timepointKeys
    # for tpNumber in range(numTimepoints):

    for tpNumber in timepointList:
        # tpIdx = int(tpNumber)  # so we can debug timepoints
        tpIdx = tpNumber
        _tpIDx = int(tpIdx)  # 20240411 not necc (Again) our keys are int

        # if tpIdx == 0:
        #     logger.info('xxx skipping tpIdx 0')
        #     continue
        
        # if tpIdx > 2:
        #     continue

        tp = map.getTimePoint(time=tpIdx)
        
        logger.info(f'ADDING tpIdx:{tpIdx} to {tp}')

        # make a df from imported csv
        segmentCsv = segmentCsvList[_tpIDx]
        dfSegments = pd.read_csv(segmentCsv, header=1)
        theseCols = ['segmentID', 'x', 'y', 'z']
        dfSegments = dfSegments[theseCols]
        
        spinesCsv = spineCsvList[_tpIDx]
        dfSpines = pd.read_csv(spinesCsv, header=1)
        theseCols = ['roiType', 'segmentID', 'x', 'y', 'z']
        dfSpines = dfSpines[theseCols]
        dfSpines = dfSpines[ dfSpines['roiType']=='spineROI' ]

        # add a number of segments (and tracing point)
        segments = dfSegments['segmentID'].unique()
        for segment in segments:
            dfSegment = dfSegments[ dfSegments['segmentID']==segment ]
            dfSpine = dfSpines[ dfSpines['segmentID']==segment ]

            # newSegmentID = map.newSegment()
            newSegmentID = tp.newSegment()
            # newSegmentID = int(newSegmentID)
            logger.info(f'=== created newSegmentID:{newSegmentID} {type(newSegmentID)} from original dfSegments["segmentID" {segment}]')

            # abb after newSegment, need to refresh/recreate ttp
            tp = map.getTimePoint(time=tpIdx)
            
            if tpIdx == _debugTpIdx:
                logger.warning(f'a) original tp is:{tp}')
                # tp = map.getTimePoint(time=tpIdx)
                logger.warning(f'b) re-fetch tp is:{tp}')

                logger.info(f'  after newSegment() tpIdx:{tpIdx} newSegmentID:{newSegmentID}')
                logger.info(f'tp is:{tp}')

            _numTracingPointsAdded = 0
            for index, row in dfSegment.iterrows():
                # do not use index, it is row label from imported df

                # add every 3rd or 4th segment point
                if _numTracingPointsAdded % addEveryPoint != 0:
                    # logger.warning(f'       !!! skipping _numTracingPointsAdded:{_numTracingPointsAdded}')
                    _numTracingPointsAdded += 1
                    continue
                
                # segmentID = row['segmentID']  # always equal to segment
                x = row['x']
                y = row['y']
                z = row['z']
                
                x = int(x)
                y = int(y)
                z = int(z)

                # map.appendSegmentPoint(newSegmentID, x, y, z)
                try:
                    # why is this in interactions.py ???
                    logger.info(f'=== appendSegmentPoint newSegmentID:{newSegmentID} x:{x} {type(x)} y:{y} z:{z}')
                    tp.appendSegmentPoint(newSegmentID, x, y, z)
        
                    # tp = map.getTimePoint(time=tpIdx)

                # fixed ???
                except (AttributeError) as e:
                    logger.error(f'NOT FIXED ERROR adding tpIdx:{tpIdx} newSegmentID:{newSegmentID} x:{x} y:{y} z:{z}')
                    logger.error(f'  error appending segment point for newSegmentID:{newSegmentID}')
                    logger.error(f'  tp is:{tp}')
                    logger.error(f'  e is:{e}')
                    raise
                    # sys.exit(1)

                _numTracingPointsAdded += 1

            if tpIdx == _debugTpIdx:
                logger.info(f'3) after add segment points for tpIdx:{tpIdx}, map is: {map}')
                logger.info(f'  added _numTracingPointsAdded:{_numTracingPointsAdded} to tpIdx:{tpIdx} newSegmentID:{newSegmentID}')
                logger.info(f'  tp is:{tp}')
                logger.info('  tp.segments[:]:')
                print(tp.segments[:])

            # logger.info('tp.segments[:] is:')
            # print(tp.segments[:])
            
            # map.segments[:]
            # abb 20241221 after newSegment, need to refresh/recreate ttp
            # tp = map.getTimePoint(time=tpIdx)

            # 20250411
            map.segments[:]

            addSpines = True  #segment == 0
            _numAddedSpines = 0
            if addSpines:
                for index, row in dfSpine.iterrows():
                    # do not use index, it is row label from iported csv

                    # add spines (0,1,2)
                    # if _numAddedSpines > 3:
                    #     break
                    
                    # segmentID = row['segmentID']  # always equal to segment
                    x = row['x']
                    y = row['y']
                    z = row['z']

                    x = int(x)
                    y = int(y)
                    z = int(z)

                    if tpIdx == _debugTpIdx:
                        logger.info(f'calling addSpine() _numAddedSpines:{_numAddedSpines} tpIdx:{tpIdx} newSegmentID:{newSegmentID} x:{x} y:{y} z:{z}')
                        logger.info(f'tp is:{tp}')

                    # 20241221 after merge with s-dev addSpine() is failing
                    # logger.info(f'addSpine() FAILING newSegmentID:{newSegmentID} x:{x} y:{y} z:{z}')
                    newSpineID = tp.addSpine(segmentId=newSegmentID, x=x, y=y, z=z)

                    # _annotations holds full map and reflect addSpine()
                    # if tpIdx == _debugTpIdx:
                    #     logger.info('after add tp._annotations.points[:]')
                    #     print(tp._annotations.points[:])
                    #     sys.exit(1)

                    # need this after each edit
                    # single tp, points/segments is NOT updated (it is a copy)
                    tp = map.getTimePoint(time=tpIdx)

                    # logger.info(f'  after add spine:{tp}')

                    # abb was in core addSpine() but giving errors
                    # 20241113, removed
                    # tp.snapBackgroundOffset(newSpineID)

                    _numAddedSpines += 1

                    if tpIdx == _debugTpIdx:
                        logger.info(f'   after addSpine() tpIdx:{tpIdx} newSegmentID:{newSegmentID}, tp is:')
                        print(f'tp:{tp}')  # call tp.__str__() -> str

                logger.warning('  === calling spine[:]')
                map.points[:]
                
                logger.info(f'   added _numAddedSpines:{_numAddedSpines} to tpIdx:{tpIdx} newSegmentID:{newSegmentID}')
                logger.info(f'   tp is:{tp}')

                # logger.error('tp.points[:] IS FAILING')
                # tp.points[:]
                
                # logger.info(f'3) after add spine points map: {map}')
                # logger.info(f'   tp.points')
                # print(tp.points)
            break
        
    return map

def understandSlicing(mapPath : str):
    map = MapAnnotations.load(mapPath)
    print(map)

    tpIdx = 1
    tp1 = map.getTimePoint(tpIdx)

    _segments = tp1.segments[:]
    print(f'_segments:{type(_segments)}')

    _points = tp1.points[:]
    print(f'_points:{type(_points)}')

    _points  = map.points[:]
    segmentID = 6
    segRows = map.points[ map.points['segmentID'] == segmentID]
    print('=== segRows')
    print(segRows[['segmentID', 'point']])
    print(segRows.index)

def tryConnectSpines():
    """Debug connect() spines from one tp to the next.
    """
    loadPath = '/Users/cudmore/Desktop/multi_timepoint_map_seg_connected.mmap'
    logger.info(f'loading: {loadPath}')
    map = MapAnnotations.load(loadPath)

    print(map)

    # fetch rows using "second" index named "t" that equals tpIdx
    # e.g. get all rows for one timepoint
    # tpIdx = 1
    # tpDf = map.points[:].xs(tpIdx, level="t")
    # print(tpDf)

    # tp0 has spines 0 .. 138
    # tp1 has spines 139 .. 271

    # single tp
    fromspineKey = (0,0)
    toSpineKey = (139,1)
    logger.info('connecting:')
    logger.info(f'   fromSpineKey:{fromspineKey}')
    logger.info(f'   toSpineKey:{toSpineKey}')
    
    # slice(start, end, step)
    # _slice = slice(toSpineKey, (139,5))
    # print('_slice:')
    # print(_slice)

    # print('=== map.points[_slice]')
    # print(map.points[_slice])

    map.connect(fromspineKey, toSpineKey)

    logger.info('=== AFTER CONNECT')
    
    tpIdx = 0
    tpDf = map.points[:].xs(tpIdx, level="t")
    print(f'tpIdx:{tpIdx}')
    print(tpDf)

    tpIdx = 1
    tpDf = map.points[:].xs(tpIdx, level="t")
    print(f'tpIdx:{tpIdx}')
    print(tpDf)

    # a run of spine id across timepoints
    _spineID = 0
    _tpDf = map.points[:].xs(_spineID, level="spineID")
    print('=== a run of connected spines')
    print(_tpDf)

def connectSegments(mapPath : str):
    """ Seg Map is
    [[0. 0. 0. 0. 0. 0. 0. 0. 0.]
    [1. 1. 1. 1. 1. 1. 1. 1. 1.]
    [2. 2. 2. 2. 2. 2. 2. 2. 2.]
    [3. 3. 3. 3. 3. 3. 3. 3. 3.]
    [4. 4. 4. 4. 4. 4. 4. 4. 4.]]
    """

    # segMapPath = '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/igorSegMapExport.npy'
    # segMapData = np.load(segMapPath)
    # print(segMapData)

    map = MapAnnotations.load(mapPath)
    print(map)

    numSegments = 5

    numTp = map.getNumTimepoints()
    for tp in range(numTp):
        if tp == numTp - 1:
            break
        
        nextTp = tp + 1
        
        for segmentIdx in range(numSegments):
            segmentID = segmentIdx + 1  # 20241222 segments are now 1 based

            # segmentKey = (segmentID + (tp * numSegments), tp)
            segmentKey = (segmentID, tp)

            toSegmentID = segmentID + (nextTp * numSegments)
            toSegmentKey = (toSegmentID, nextTp)

            logger.info(f'tp:{tp} segmentKey:{segmentKey} toSegmentKey:{toSegmentKey}')

            map.connectSegment(segmentKey=segmentKey, toSegmentKey=toSegmentKey)

            # map.segments[:]
            # print(map.segments[:].index)

    map.points[:]
    map.segments[:]
    return map

def run(numTimepoints : int):
    map = createMap(numTimepoints=numTimepoints)

    # add segments and spines to map
    map = loadSegments(map)

    logger.info('=== FINAL MAP IS:')
    print(map)

    logger.info(f'  === calling points[:]')
    map.points[:]
    
    logger.info(f'  === calling segments[:]')
    map.segments[:]


    logger.info(f'   === points is:')
    print(map.points[:])

    logger.info(f'   === segments is:')
    print(map.segments[:])

    logger.info(f'  === segment.columns are:')
    print(map.segments[:].columns)

    # _date = '20250322'
    _date = '20250411'
    if numTimepoints== 1:
        savePath = f'/Users/cudmore/Desktop/single_timepoint_{_date}.mmap'
        saveZipPath = f'/Users/cudmore/Desktop/single_timepoint_{_date}.mmap.zip'
    else:
        savePath = '/Users/cudmore/Desktop/multi_timepoint_seg.mmap'
        saveZipPath = '/Users/cudmore/Desktop/multi_timepoint_seg.zip.mmap'
    print(f'savePath:{savePath}')
    map.save(savePath)
    # map.save(saveZipPath)

    # this was just testing a few connections
    # tryConnectSpines()

    # understandSlicing(savePath)

    # now use connectSpines.py

    # test_load(savePath)
    return savePath

# def loadAndSaveAsZip():
#     loadPath = '/Users/cudmore/Desktop/single_timepoint.mmap'
#     map= MapAnnotations.load(path=loadPath)

#     saveZipPath = '/Users/cudmore/Desktop/single_timepoint.zip.mmap'
#     print(f'saveZipPath:{saveZipPath}')
#     map.save(saveZipPath, compression='zip')

def test_load(path:str):
    logger.info(f'path:{path}')

    ma = MapAnnotations.load(path)

def connectSegments2():
    loadPath = '/Users/cudmore/Desktop/multi_timepoint_seg.mmap'
    segmentMap = connectSegments(loadPath)
    
    savePath = '/Users/cudmore/Desktop/multi_timepoint_seg_connected.mmap'
    print(f'savePath:{savePath}')
    segmentMap.save(savePath)

    saveZipPath = '/Users/cudmore/Desktop/multi_timepoint_seg_connected.zip.mmap'
    # segmentMap.save(saveZipPath, compression='zip')

if __name__ == '__main__':
    # 1) make a multi timepoint map
    
    # numTimepoints = 5
    numTimepoints = 1
    savedPath = run(numTimepoints)    

    path = '/Users/cudmore/Desktop/single_timepoint_20250411.mmap'
    test_load(path)

    # connect xsegment in multi timepoint map
    # connectSegments2()

    # creatZarrLoader(1)

    # test_load('/Users/cudmore/Desktop/single_timepoint_20250108.mmap')