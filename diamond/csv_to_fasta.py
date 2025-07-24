import csv
import os

def csv_to_fasta(csv_name, fasta_name):
    """Convert a CSV file to FASTA format.
    Assumes CSV columns: ID, EC Number, Sequence (in that order).
    """
    with open(csv_name, 'r') as csvfile, open(fasta_name, 'w') as outfile:
        csvreader = csv.reader(csvfile, delimiter='\t')
        for i, row in enumerate(csvreader):
            if i > 0:  # Skip header row
                outfile.write(f">{row[0]}\n")  # Write sequence ID
                outfile.write(f"{row[2]}\n")   # Write sequence data

def batch_csv_to_fasta(input_folder, output_folder):
    """Batch convert all CSV files in a directory to FASTA format.
    
    Args:
        input_folder: Directory containing input CSV files.
        output_folder: Directory to save output FASTA files.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            # Build full file paths
            csv_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]  # Remove extension
            fasta_path = os.path.join(output_folder, f"{base_name}.fasta")
            
            # Convert CSV to FASTA
            csv_to_fasta(csv_path, fasta_path)
            print(f"Converted: {filename} → {base_name}.fasta")

# Main execution
if __name__ == "__main__":
    # Batch convert EC-number split CSV files to FASTA format
    batch_csv_to_fasta(
        "./data_split30/57w_ec_split_csv",
        "./data_split30/57w_ec_split_fasta"
    )

