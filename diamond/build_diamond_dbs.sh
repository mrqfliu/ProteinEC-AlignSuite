#!/bin/bash

# Batch create DIAMOND databases for protein sequence alignment
# This script processes all FASTA files in a directory to generate .dmnd databases

# Iterate over all FASTA files in the specified directory
for fasta_file in /dellfsqd2/ST_OCEAN/USER/liuqifan/ec_split_dataset_fasta/*.fasta; do
    # Extract the base filename without path
    filename=$(basename "$fasta_file")
    
    # Generate database name by removing the file extension
    db_name="${filename%.*}"
    
    # Define the output path for the DIAMOND database
    output_db="/dellfsqd2/ST_OCEAN/USER/liuqifan/ec_split_dataset_dmnd/${db_name}.dmnd"
    
    # Create DIAMOND database using the input FASTA file
    /dellfsqd2/ST_OCEAN/USER/liliangwei/scripts/Annotation_2016a/bin/common_bin/diamond makedb --in "$fasta_file" --db "$output_db"
    
    # Log progress
    echo "Database created: $output_db (from $filename)"
done