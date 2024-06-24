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