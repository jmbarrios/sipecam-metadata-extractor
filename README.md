# sipecam-metadata-extractor

## Running `sipecam/simex/` docker image in CONABIO cluster 

### Commands of `simex`

Set:

```
SIMEX_VERSION=0.1
REPO_URL=sipecam/simex
CONTAINER_NAME=sipecam-simex
```

Command `list_of_files_to_extract_metadata`

```
dir_with_sipecam_data=/LUSTRE/sacmod/SIPECAM/Entregas_2021/octubre_2021/SIPECAM/
docker run --rm -v /LUSTRE:/LUSTRE -v $HOME:/shared_volume --name $CONTAINER_NAME -d $REPO_URL:$SIMEX_VERSION list_of_files_to_extract_metadata --input_directory $dir_with_sipecam_data
```

Command `extract_metadata_and_ingest_it`

```
file_to_be_processed=$(head -n 1 ~/sipecam_files_to_extract_metadata_from_*)
docker run --rm -v /LUSTRE:/LUSTRE -v $HOME:/shared_volume --name $CONTAINER_NAME -d $REPO_URL:$SIMEX_VERSION extract_metadata_and_ingest_it --input_file "$file_to_be_processed"
```

## Running `sipecam/simex/` docker image in a docker container `jupyterlab` cmd

```
docker run --rm -v $HOME:/shared_volume --name $CONTAINER_NAME -p 3000:8888 -d $REPO_URL:$SIMEX_VERSION /usr/local/bin/jupyter lab --ip=0.0.0.0 --no-browser --allow-root
```
