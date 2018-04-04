# Scripts for Frontiers Paper

Each directory contains scripts that create output TSV files for their associated analysis.  They each include a `run.sh` file which is the entrypoint to that set of analysis.  A description of each directory along with output is below:

## Setup
To start, **you must set the `DB_CONFIG`** environment variable to the path for an ImmuneDB database configuration.  To use the database from the paper, set this to the path of the included `public_frontiers.json` file.

Then, in the root directory run:
```
pip install -r requirements.txt
```

## `copy_cutoff`: Clone copy numbers 
### Usage
```
bash run.sh
```
### Output
One `copy_cutoff` TSV per subject with the number of copies and the fraction of the clonal repertoire containing that many copies.

## `cosine_sim`: Pairwise cosine similarity
### Usage
```
bash run.sh SUBJECT_IDENTIFIER
```
### Example
```
bash run.sh D207
```
### Output
There will be ten files output with names in the form `similarity_C`**instances**`_`**metric**`.tsv` where **instances** is the minimum number of instances (ranging from 1 to 5) and **metric** is the magnitude metric (`copies` and `instances`).  Each file contains cosine similarities between each pair of samples in the specified subject.

## `diversity`: Rarefaction and diversity
You must install the [diversity](https://github.com/GregorySchwartz/diversity) package for this set of analyses.
### Usage
```
bash run.sh
```
### Output
**Rarefaction**: There will be an output file for each subject **subject**  and minimum instances **instances** (ranging from 1 to 5) in the form **subject**`_C`**instances**`.tsv`.  Each file contains the sample-based expected richness at each subsample.

**Diversity**: There will be two files, `diversity_copies.tsv` and `diversity_instances.tsv` which has the diversity at each subject/instance count/hill number.

## `gene_usage`: V-gene usage
### Usage
```
bash run.sh
```
### Output
There will be a `usage.tsv` file which specifies the V-gene usage frequency for each subject.  The frequency is given weighing each clone by three metrics: `clones` equally weighs each clone as 1, `clones_uniques` weighs each clone by number of unique sequences, `clones_instances` weighs each clone by number of instances, and `clones_copies` weighs each clone by copy number.

## `metrics`: Miscellaneous metrics
### Usage
```
bash run.sh SUBJECT_IDENTIFIER
```
### Example
```
bash run.sh D207
```
### Output
One file **subject**`_metrics.tsv` will contain various clonal metrics for instance cutoffs 1 through 20.

## `shm`: Somatic hypermutation
### Usage
```
bash run.sh SUBJECT_IDENTIFIER
```
### Output
The file `shm.tsv` will contain counts of replacement and silent mutations for each clone in the database.
