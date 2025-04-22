## Sample data for MapManager

See this and that

## Notes

To add to Github LFS

git lfs track "*.mmap"  

.gitattributes file is

```
*.tif filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
*.mmap filter=lfs diff=lfs merge=lfs -text
```

List all files in local git

git ls-tree --full-tree -r --name-only HEAD

# making zip version of mmap

To make an mmap zip from the command line. This zips without outer folder and with no compression (zarr folder is already compressed)

If you have a mmap folder like `my_mm_map.zarr/`.

```
cd my_mm_map.zarr
zip -r0 ../my_mm_map.zarr.zip ./

# 202504 we have two maps we want to zip

    cd data/202504/single_timepoint_202504.mmap
    zip -r0 ../single_timepoint_202504.mmap.zip ./     

## Change Log

20250204
 - added Olsen raw nd2 file and mmap