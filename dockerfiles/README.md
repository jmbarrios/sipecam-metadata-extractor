Set:

```
JUPYTERLAB_VERSION=3.2.4
REPO_URL=sipecam/simex
DIR=/home/<user>/<midir>/sipecam-metadata-extractor/ #path where this git repository is cloned, example: /home/user/sipecam-metadata-extractor
BUILD_DIR=$DIR/dockerfiles/$JUPYTERLAB_VERSION
CONTAINER_NAME=sipecam-simex
```

Clone:

```
git clone https://github.com/CONABIO/sipecam-metadata-extractor.git $DIR
```

Build:

```
docker build $BUILD_DIR --force-rm -t $REPO_URL:$JUPYTERLAB_VERSION
```

## Running `sipecam/simex/` docker image in CONABIO cluster 

### Commands of `simex`

```
dir_with_sipecam_data=/LUSTRE/sacmod/SIPECAM/Entregas_2021/octubre_2021/SIPECAM/
docker run --rm -v $HOME:/shared_volume --name $CONTAINER_NAME -d $REPO_URL:$JUPYTERLAB_VERSION list_of_files_to_extract_metadata --input_directory $dir_with_sipecam_data
```

```
file_to_be_processed=$(head -n 1 ~/sipecam_files_to_extract_metadata_from_*)
docker run --rm -v $HOME:/shared_volume --name $CONTAINER_NAME -d $REPO_URL:$JUPYTERLAB_VERSION extract_metadata_and_ingest_it --input_file "$file_to_be_processed"
```

## Running `sipecam/simex/` docker image in a docker container `jupyterlab` cmd

```
docker run --rm -v $HOME:/shared_volume --name $CONTAINER_NAME -p 3000:8888 -d $REPO_URL:$JUPYTERLAB_VERSION /usr/local/bin/jupyter lab --ip=0.0.0.0 --no-browser --allow-root
```

## jupyter lab running at localhost:3000

(not necessary) Enter to docker container with:

```
docker exec -it -u=simexuser $CONTAINER_NAME bash
```

Stop:

```
docker stop $CONTAINER_NAME
```

Delete (if `--rm` wasn't used):


```
docker rm $CONTAINER_NAME
```

