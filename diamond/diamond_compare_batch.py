import os
import subprocess

# Set input folder paths
fasta_dir = "/dellfsqd2/ST_OCEAN/USER/liuqifan/ec_split_dataset_fasta"
dmnd_dir = "/dellfsqd2/ST_OCEAN/USER/liuqifan/ec_split_dataset_dmnd"
output_file = "/dellfsqd2/ST_OCEAN/USER/liuqifan/ec_split_dataset_result/all_results.m8"  # Unified output file

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Open the unified output file for writing
with open(output_file, "w") as outfile:
    # Iterate over all files in the fasta directory
    for fasta_file in os.listdir(fasta_dir):
        if fasta_file.endswith(".fasta"):
            # Construct the path to the corresponding dmnd file
            base_name = os.path.splitext(fasta_file)[0]
            dmnd_file = os.path.join(dmnd_dir, base_name + ".dmnd")
            
            # Check if the corresponding dmnd file exists
            if not os.path.exists(dmnd_file):
                print(f"Warning: No corresponding DMND file found for {fasta_file}. Skipping...")
                continue
            
            # Execute the diamond blastp command and append results to the unified output file
            cmd = [
                "/dellfsqd2/ST_OCEAN/USER/liliangwei/scripts/Annotation_2016a/bin/common_bin/diamond", "blastp", "-k", "2", "--threads", "4",
                "-d", dmnd_file,
                "-q", os.path.join(fasta_dir, fasta_file),
                "--sensitive",
                "--outfmt", "6", "qseqid", "sseqid", "pident"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check if the command executed successfully
            if result.returncode != 0:
                print(f"Error occurred while processing {fasta_file}: {result.stderr}")
                continue
            
            # Write the results to the unified output file
            outfile.write(result.stdout)
            print(f"Processed {fasta_file} and appended results to {output_file}")