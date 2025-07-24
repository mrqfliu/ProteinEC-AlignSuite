import os
import csv
import signal
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Tuple
from tqdm import tqdm

@dataclass
class Config:
    csv_dir: Path
    protein_dir: Path
    output_base: Path
    parallel_jobs: int = 8
    valid_extensions: Tuple[str] = ('.pdb', '.pdb.gz')  # Supported file extensions

class PDBOrganizer:
    def __init__(self, config: Config):
        self.config = config
        self.running = True
        self.file_index: Dict[str, List[Path]] = {}  # Store file paths for each base name
        self._register_signals()
        self.config.output_base.mkdir(parents=True, exist_ok=True)

    def _register_signals(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\nInterruption signal captured, performing cleanup...")
        self.running = False
        sys.exit(1)

    def build_file_index(self):
        """Build an index of files with all possible extensions"""
        print("Scanning PDB files...")
        for root, _, files in os.walk(self.config.protein_dir):
            for file in files:
                # Check both filename pattern and valid extensions
                if file.startswith("AF-") and "-F1-model_v4" in file:
                    # Split filename and extension
                    for ext in self.config.valid_extensions:
                        if file.endswith(ext):
                            # Extract base name (remove extension)
                            base_name = file[:-len(ext)].rstrip('.')  # Handle possible extra dots
                            full_path = Path(root) / file
                            
                            # Add to index
                            if base_name not in self.file_index:
                                self.file_index[base_name] = []
                            self.file_index[base_name].append(full_path)
                            break

    def process_ec_dataset(self):
        """Process all EC classifications"""
        ec_files = list(self.config.csv_dir.glob("EC_*.csv"))
        with tqdm(total=len(ec_files), desc="Processing EC Classes") as main_pbar:
            for csv_file in ec_files:
                if not self.running:
                    break
                self.process_single_ec(csv_file)
                main_pbar.update(1)

        print("\nProcessing complete. Generated EC database structure:")
        os.system(f"tree -h {self.config.output_base}")

    def process_single_ec(self, csv_file: Path):
        """Process a single EC classification"""
        ec_number = csv_file.stem.split("_")[1]
        ec_dir = self.config.output_base / ec_number
        ec_dir.mkdir(exist_ok=True)

        # Get target file list
        target_ids = self.parse_csv(csv_file)
        target_files = []
        
        for pid in target_ids:
            base_name = f"AF-{pid}-F1-model_v4"
            if base_name in self.file_index:
                # Prefer .pdb files if available, otherwise use the first available format
                preferred = next(
                    (p for p in self.file_index[base_name] if p.suffix == '.pdb'),
                    self.file_index[base_name][0]  # Default to first file
                )
                target_files.append(preferred)

        # Create progress bar
        with tqdm(total=len(target_files), desc=f"EC {ec_number}", 
                 leave=False, position=1) as pbar:
            
            with ThreadPoolExecutor(max_workers=self.config.parallel_jobs) as executor:
                futures = []
                for src in target_files:
                    futures.append(executor.submit(
                        self.create_symlink, src, ec_dir, pbar
                    ))
                
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"\nError: {str(e)}")

    def parse_csv(self, csv_file: Path) -> List[str]:
        """Parse CSV file to get PDB ID list"""
        pdb_ids = []
        with open(csv_file) as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Skip header row
            for row in reader:
                if row:
                    pdb_ids.append(row[0])
        return pdb_ids

    def create_symlink(self, src: Path, dest_dir: Path, pbar: tqdm):
        """Create symbolic link while preserving original filename (including extension)"""
        try:
            dest = dest_dir / src.name
            if not dest.exists():
                relative_src = os.path.relpath(src, dest_dir)
                dest.symlink_to(relative_src)
            pbar.update(1)
        except Exception as e:
            raise RuntimeError(f"Failed to create link: {src} -> {dest_dir}: {str(e)}")

if __name__ == "__main__":
    config = Config(
        csv_dir=Path("./ec_split_dataset_csv"),
        protein_dir=Path("/ldfsqd1/ST_OCEAN/USER/proteinDB/sprot_pdbs"),
        output_base=Path("./ec_databases"),
        parallel_jobs=8
    )

    organizer = PDBOrganizer(config)
    organizer.build_file_index()
    organizer.process_ec_dataset()