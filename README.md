# ProteinEC-AlignSuite

A tool suite for batch structural (Foldseek) and sequence (Diamond) alignment of proteins grouped by EC numbers, with preconfigured paths in code for simplified usage.


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Foldseek Structural Alignment Pipeline](#foldseek-structural-alignment-pipeline)
  - [Diamond Sequence Alignment Pipeline](#diamond-sequence-alignment-pipeline)
- [Directory Structure](#directory-structure)
- [Output Description](#output-description)


## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mrqfliu/ProteinEC-AlignSuite.git
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
Edit the following files to set your data paths:
- **Main Script (Shared by Both Pipelines)**:
  - `split_data_same_lables.py`: Set input CSV path and output EC-CSV directory.

- **Foldseek Pipeline Scripts (in `foldseek/`)**:
  - `pdb_data_split.py`: EC-CSV directory, raw PDB folder, output EC database directory.
  - `foldseek_batch_create_db.py`: EC database directory, Foldseek DB output directory.
  - `foldseek_library_compare.py`: Foldseek DB directory, alignment output directory.

- **Diamond Pipeline Scripts (in `diamond/`)**:
  - `csv_to_fasta.py`: Input EC-CSV directory, output FASTA directory.
  - `build_diamond_dbs.sh`: Input FASTA directory, Diamond DB output directory.
  - `diamond_compare_batch.py`: FASTA directory, Diamond DB directory, merged result path.


## Usage

### Foldseek Structural Alignment Pipeline
```bash
# Step 1: Split CSV by EC number (run from main directory)
python split_data_same_lables.py

# Step 2-5: Run Foldseek pipeline (run from main directory)
python foldseek/pdb_data_split.py
python foldseek/foldseek_batch_create_db.py
python foldseek/foldseek_library_compare.py
cat ./alignments/*/align.m8 > ./foldseek_merged_results.m8
```


### Diamond Sequence Alignment Pipeline
```bash
# Step 1: Split CSV by EC number (run from main directory)
python split_data_same_lables.py

# Step 2-4: Run Diamond pipeline (run from main directory)
python diamond/csv_to_fasta.py
bash diamond/build_diamond_dbs.sh
python diamond/diamond_compare_batch.py
```


## Directory Structure
```
ProteinEC-AlignSuite/
├── split_data_same_lables.py          # Main script for EC splitting (shared)
├── foldseek/                          # Foldseek pipeline scripts
│   ├── pdb_data_split.py              # Organize PDB files by EC
│   ├── foldseek_batch_create_db.py    # Build Foldseek databases
│   ├── foldseek_library_compare.py    # Run Foldseek alignments
|   └── alignments/                    # Foldseek alignment results
└── diamond/                           # Diamond pipeline scripts
    ├── csv_to_fasta.py                # Convert CSV to FASTA
    ├── build_diamond_dbs.sh           # Build Diamond databases
    ├── diamond_compare_batch.py       # Run Diamond alignments
    └── ec_split_dataset_result/       # Diamond alignment results
```


## Output Description
- **Foldseek Results**:  
  Structural alignments are saved in `./alignments` (one subdirectory per EC class, containing `align.m8` with fields like `alntmscore`, `lddt`, `evalue`).

- **Diamond Results**:  
  Sequence alignments are merged into `./ec_split_dataset_result/all_results.m8` (fields include `qseqid`, `sseqid`, `pident`, `evalue`).

All outputs use standard tab-separated (M8) format, compatible with pandas, R, or Excel for downstream analysis.
