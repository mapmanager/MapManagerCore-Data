import os
from pprint import pprint
import pandas as pd

from mapmanagercore.data import getTiffChannel_1, getTiffChannel_2

from mapmanagercore import MapAnnotations, mmMapLoader
from mapmanagercore.logger import logger

def grab_sparse_tracing():
    segmentCsv = '/Users/cudmore/Sites/PyMapManager-Data/maps/rr30a/rr30a_s0/rr30a_s0_la.txt'
    if not os.path.isfile(segmentCsv):
        logger.error(f'file not found: {segmentCsv}')
        return
    dfSegments = pd.read_csv(segmentCsv, header=1)
    theseCols = ['segmentID', 'x', 'y', 'z']
    dfSegments = dfSegments[theseCols]
    # print(dfSegments)

    addEveryPoint = 4

    outDf = pd.DataFrame(columns=['segmentID', 'x', 'y', 'z'])

    segments = dfSegments['segmentID'].unique()
    segments = [0]  # just the first imported segment
    for importSegmentID in segments:
        dfSegment = dfSegments[ dfSegments['segmentID']==importSegmentID ]

        _numTracingPointsAdded = 0

        for importRowIdx, row in dfSegment.iterrows():
            # do not use index, it is row label from imported df

            # add every 3rd or 4th segment point
            if _numTracingPointsAdded % addEveryPoint != 0:
                # logger.warning(f'       !!! skipping _numTracingPointsAdded:{_numTracingPointsAdded}')
                _numTracingPointsAdded += 1
                continue
            
            x = int(row['x'])
            y = int(row['y'])
            z = int(row['z'])

            rowDict = {
                'segmentID': importSegmentID,
                'x': x,
                'y': y,
                'z': z,
            }
            new_row = pd.DataFrame([rowDict])
            outDf = pd.concat([outDf, new_row], ignore_index=True)

            _numTracingPointsAdded += 1
    #
    print(outDf)
    savePath = 'data/202504/sparse_segment.csv'
    logger.info(f'saving to: {savePath}')
    outDf.to_csv(savePath, index=False)

def test_empty_map():
    path1 = getTiffChannel_1()
    path2 = getTiffChannel_2()
    
    logger.info(f' creating empty loader')
    loader = mmMapLoader()

    logger.info('  import first timepoint, seeded with imgData')
    _newTimepoint = loader.importTimepoint(path1)
    assert _newTimepoint == 1

    # append another channel
    if 1:
        logger.info('  adding second channel')
        _channel = loader.importChannel(path2, timepoint=_newTimepoint)
        logger.info(f'    2nd channel is _channel:{_channel}')
        assert loader.numChannels(_newTimepoint) == 2

    logger.info('== creating MapAnnotations from loader')
    mmap = MapAnnotations(loader,
                         lineSegments=pd.DataFrame(),
                         points = pd.DataFrame())

    print(mmap)

    # analysisParameters = mmap.loader.metadata.getTimepoint(1).analysisParameters
    # _dict = analysisParameters.to_dict_with_metadata()
    # pprint(_dict, sort_dicts=False)

    # return

    savePath = 'data/202504/empty_map_202504.mmap'
    logger.info('=== saving mmap:{savePath}')
    mmap.save(savePath)

    logger.info('=== reload the map')
    mmap = MapAnnotations.load(savePath)
    logger.info(f'after reload mmap is:')
    print(mmap)

    # zip -r0 ./data/202504/empty_map_202504.mmap.zip ./data/202504/empty_map_202504.mmap/.

if __name__ == '__main__':
    test_empty_map()
    # grab_sparse_tracing()