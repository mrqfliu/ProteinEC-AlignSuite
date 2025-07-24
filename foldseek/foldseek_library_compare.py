import os
from pathlib import Path
import subprocess
from tqdm import tqdm
import re

class AlignConfig:
    def __init__(self):
        self.foldseek_bin = Path("/dellfsqd2/ST_OCEAN/USER/wangdantong/projects/toolbox/foldseek/bin/foldseek")  # Path to Foldseek executable
        self.db_dir = Path("./ec_create_db")  # Directory containing EC databases
        self.output_root = Path("./alignments")  # Root directory for alignment results
        self.threads = 8  # Number of threads for alignment

def run_self_alignment(config: AlignConfig):
    """Perform self-alignment for all EC databases using Foldseek"""
    # Create output root directory if it doesn't exist
    config.output_root.mkdir(exist_ok=True)

    # Regex pattern to match EC database files (adjust based on actual naming)
    # Matches files like "ec_1_1_1_1.dbtype" derived from EC numbers (e.g., 1.1.1.1)
    main_db_pattern = re.compile(r'^ec_([^_]+_){3}[^_]+\.dbtype$')

    # Get all valid EC database files (filter by .dbtype suffix)
    db_files = [
        p for p in config.db_dir.glob("*.dbtype")
        if main_db_pattern.match(p.name)
    ]
    
    if not db_files:
        print("No EC database files found")
        return

    # Initialize progress bar
    with tqdm(
        db_files,
        desc="Processing EC Databases",
        unit="DB",
        ncols=100,
        colour="#00ff00",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    ) as pbar:
        for db_path in pbar:
            # Extract EC database name (without .dbtype suffix)
            ec_name = db_path.stem
            # Create output directory for current EC database
            output_dir = config.output_root / ec_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get database prefix (critical: removes .dbtype suffix for Foldseek compatibility)
            db_prefix = str(db_path.with_suffix(''))

            # Construct Foldseek easy-search command for self-alignment
            cmd = [
                str(config.foldseek_bin), "easy-search",
                str(db_prefix), str(db_prefix),  # Query and target: same database (self-alignment)
                str(output_dir / "align.m8"),  # Output alignment results
                str(output_dir / "tmp"),  # Temporary directory for intermediate files
                "--threads", str(config.threads),  # Number of threads
                "--max-accept", "2",  # Max acceptable alignments per query
                "--format-output", "query,target,alntmscore,qtmscore,ttmscore,lddt,prob,fident,alnlen,evalue"  # Custom output fields
            ]

            # Update progress bar with current EC database
            pbar.set_postfix_str(f"Processing: {ec_name}")

            try:
                # Execute command (run directly without capturing output)
                subprocess.run(
                    cmd,
                    check=True  # Raise error if command fails
                )
                pbar.set_postfix_str(f"{ec_name} ✅", refresh=True)
            except subprocess.CalledProcessError as e:
                pbar.set_postfix_str(f"{ec_name} ❌ Error code: {e.returncode}", refresh=True)

if __name__ == "__main__":
    config = AlignConfig()

    # Validate Foldseek executable exists
    if not config.foldseek_bin.exists():
        print(f"Error: Foldseek not found at {config.foldseek_bin}")
        exit(1)

    # Run self-alignment pipeline
    run_self_alignment(config)