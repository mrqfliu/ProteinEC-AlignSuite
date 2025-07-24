# ProteinEC-AlignSuite

A tool suite for batch structural (Foldseek) and sequence (Diamond) alignment of proteins grouped by EC numbers, with preconfigured paths in code for simplified usage.


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Foldseek Structural Alignment Pipeline](#foldseek-structural-alignment-pipeline)
  - [Diamond Sequence Alignment Pipeline](#diamond-sequence-alignment-pipeline)
- [Output Description](#output-description)


## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ProteinEC-AlignSuite.git
cd ProteinEC-AlignSuite
```

### 2. Create and Activate Environment
```bash
# Create conda environment (Python 3.8+)
conda create -n proteinec-align python=3.8 -y
conda activate proteinec-align

# Install dependencies
pip install tqdm
```

### 3. Configure Paths (Critical Step)
All input/output paths are preconfigured in the scripts. Before running, edit the following files to set your data paths:
- `split_data_same_lables.py`: Set input CSV path and output EC-CSV directory.
- `pdb_data_split.py`: Set paths for EC-CSV directory, raw PDB folder, and output EC database directory.
- `foldseek_batch_create_db.py`: Set paths for EC database directory and Foldseek DB output directory.
- `foldseek_library_compare.py`: Set paths for Foldseek DB directory and alignment output directory.
- `csv_to_fasta.py`: Set input EC-CSV directory and output FASTA directory.
- `build_diamond_dbs.sh`: Set input FASTA directory and Diamond DB output directory.
- `diamond_compare_batch.py`: Set paths for FASTA directory, Diamond DB directory, and merged result path.


## Usage

### Foldseek Structural Alignment Pipeline
Processes protein structures within the same EC class for structural similarity comparison.

#### Step 1: Split CSV Files by EC Number
Split the original protein dataset into EC-specific sub-files (paths preconfigured in script):
```bash
python split_data_same_lables.py
```


#### Step 2: Organize PDB Files by EC Class
Create symbolic links to group PDB files by EC number (paths preconfigured in script):
```bash
python pdb_data_split.py
```


#### Step 3: Build Foldseek Databases for Each EC Class
Batch-create Foldseek structural databases (paths preconfigured in script):
```bash
python foldseek_batch_create_db.py
```


#### Step 4: Run Structural Alignment Within EC Classes
Perform self-alignment for each EC database to compare structures (paths preconfigured in script):
```bash
python foldseek_library_compare.py
```


#### Step 5: Merge Alignment Results (Optional)
Combine all EC alignment results into a single file:
```bash
cat ./alignments/*/align.m8 > ./foldseek_merged_results.m8
```


### Diamond Sequence Alignment Pipeline
Processes protein sequences within the same EC class for sequence similarity comparison.

#### Step 1: Split CSV Files by EC Number (Reuse Foldseek Step 1)
If you already ran the Foldseek pipeline, skip this step. Otherwise:
```bash
python split_data_same_lables.py
```


#### Step 2: Convert CSV Files to FASTA Format
Convert EC-specific CSV files to FASTA sequences (paths preconfigured in script):
```bash
python csv_to_fasta.py
```


#### Step 3: Build Diamond Databases
Batch-create Diamond sequence databases (paths preconfigured in script):
```bash
bash build_diamond_dbs.sh
```


#### Step 4: Run Sequence Alignment Within EC Classes
Perform batch BLASTP alignment for each EC database (paths preconfigured in script):
```bash
python diamond_compare_batch.py
```


## Output Description
- **Foldseek Results**: Structural alignments are saved in `./alignments` (one subdirectory per EC class, each containing `align.m8` with fields like `alntmscore`, `lddt`, and `evalue`).
- **Diamond Results**: Sequence alignments are merged into `./ec_split_dataset_result/all_results.m8` (fields include `qseqid`, `sseqid`, `pident`, and `evalue`).

All outputs use standard tab-separated (M8) format, compatible with downstream tools like pandas or R for analysis.
