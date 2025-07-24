import csv
from collections import defaultdict

# Initialize a dictionary to store data rows for each EC number
ec_datasets = defaultdict(list)

# Read the original TSV file
with open('./benchmark_data/57w_filtered_ec_labels_clean.csv', 'r', newline='') as infile:
    reader = csv.reader(infile, delimiter='\t')
    header = next(reader)  # Read the header row
    for row in reader:
        ec_numbers = row[1]
        # Split multiple EC numbers
        for ec in ec_numbers.split(';'):
            ec_clean = ec.strip()
            ec_datasets[ec_clean].append(row)

# Generate a CSV file for each EC number
for ec, rows in ec_datasets.items():
    filename = f"./data_split30/57w_ec_split_csv/EC_{ec}.csv"
    with open(filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(header)  # Write the header
        writer.writerows(rows)   # Write the data rows
