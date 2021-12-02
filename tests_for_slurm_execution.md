# Running `sipecam/simex:0.1` docker image in CONABIO cluster (test)

Ssh to one node of CONABIO cluster as user `madmex_admin`.

## Parallel-ssh to rmi and pull docker image for each node at CONABIO

Create `~/nodos.txt`

```
nodo1
nodo2
nodo3
nodo4
nodo5
nodo6
nodo7
```

then:

```
SIMEX_VERSION=0.1
REPO_URL=sipecam/simex
parallel-ssh -i -p 2 -v -h nodos.txt -l madmex_admin "docker rmi $REPO_URL:$SIMEX_VERSION; docker pull $REPO_URL:$SIMEX_VERSION"
```

**Every time metadata will be extracted run last command of `parallel-ssh` (setting env variables) to download latest docker image of `sipecam/simex`.**


## Using `slurm` (test)

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

Check number of files whose metadata will be extracted

```
wc -l sipecam_files_to_extract_metadata_from_02-12-2021.txt
```

### Create slurm jobs

Only first time: create `~/slurm_extract_metadata_and_ingest_it.sh`

```
#!/bin/bash
# first parameter is file whose metadata will be extracted

#SBATCH --ntasks=1           # total processes across nodes
#SBATCH --ntasks-per-node=1
#SBATCH --requeue

SIMEX_VERSION=0.1
REPO_URL=sipecam/simex

echo "$1"
docker run --rm -v /LUSTRE:/LUSTRE -v $HOME:/shared_volume -d $REPO_URL:$SIMEX_VERSION extract_metadata_and_ingest_it --input_file "$1"
```

### Test 1

```
file_to_be_processed_1=$(head -n 1 ~/sipecam_files_to_extract_metadata_from_02-12-2021.txt)
bash ~/slurm_extract_metadata_and_ingest_it.sh "$file_to_be_processed_1"
```

Wait 10 secs (approx).

```
dirname_file_to_be_processed_1=$(dirname "$file_to_be_processed_1")
temp_dir_for_logs_1=$(find "$dirname_file_to_be_processed_1" -name 'temp*')
basename_file_to_be_processed_1=$(basename "$file_to_be_processed_1")
cat "$temp_dir_for_logs_1/logs_$basename_file_to_be_processed_1"
```

Delete dir

```
rm -rf "$temp_dir_for_logs_1"
```

### (End Test 1)

Create directory with name of date of launch:

```
today_date=$(printf '%(%d-%m-%Y)T\n' -1)
mkdir test_sipecam_extract_metadata_$today_date
```

Create shell inside: `~/test_sipecam_extract_metadata_$today_date/test_script_to_generate_slurm_jobs.sh`

```
#!/bin/bash
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
today_date=$(printf '%(%d-%m-%Y)T\n' -1)

for f in $(head -n 2 ~/sipecam_files_to_extract_metadata_from_$today_date.txt)
do
  echo "sbatch -D ~/test_sipecam_extract_metadata_$today_date ~/slurm_extract_metadata_and_ingest_it.sh \""$f"\"" >> ~/test_sipecam_extract_metadata_$today_date/test_slurm_jobs_extract_metadata_and_ingest_it.sh
done
IFS=$SAVEIFS

```

Get jobs that will be executed with `slurm`

```
bash ~/test_sipecam_extract_metadata_$today_date/test_script_to_generate_slurm_jobs.sh
```

Check number of jobs that will be launched will slurm

```
wc -l ~/test_sipecam_extract_metadata_$today_date/test_slurm_jobs_extract_metadata_and_ingest_it.sh
```


### Test 2

Launch this subset of jobs

```
bash ~/test_sipecam_extract_metadata_$today_date/test_slurm_jobs_extract_metadata_and_ingest_it.sh
```

Check logs of slurm inside `~/test_sipecam_extract_metadata_$today_date`

Check running jobs

```
squeue -u madmex_admin
```

Check logs of metadata extraction command.

```
file_to_be_processed_1=$(head -n 1 ~/sipecam_files_to_extract_metadata_from_02-12-2021.txt)
dirname_file_to_be_processed_1=$(dirname "$file_to_be_processed_1")
temp_dir_for_logs_1=$(find "$dirname_file_to_be_processed_1" -name 'temp*')
basename_file_to_be_processed_1=$(basename "$file_to_be_processed_1")
cat "$temp_dir_for_logs_1/logs_$basename_file_to_be_processed_1"

file_to_be_processed_2=$(head -n 2 ~/sipecam_files_to_extract_metadata_from_02-12-2021.txt|tail -n 1)
dirname_file_to_be_processed_2=$(dirname "$file_to_be_processed_2")
temp_dir_for_logs_2=$(find "$dirname_file_to_be_processed_2" -name 'temp*')
basename_file_to_be_processed_2=$(basename "$file_to_be_processed_2")
cat "$temp_dir_for_logs_2/logs_$basename_file_to_be_processed_2"

```

Delete dirs

```
rm -rf "$temp_dir_for_logs_1"
rm -rf "$temp_dir_for_logs_2"
```

### (End Test 2)

