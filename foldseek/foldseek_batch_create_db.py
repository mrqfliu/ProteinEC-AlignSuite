import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from tqdm import tqdm
import re

@dataclass
class FoldseekConfig:
    foldseek_bin: Path = Path("/dellfsqd2/ST_OCEAN/USER/wangdantong/projects/toolbox/foldseek/bin/foldseek")  # Path to foldseek executable
    ec_input_dir: Path = Path("./ec_databases")  # Input directory containing EC-classified folders
    db_output_dir: Path = Path("./ec_create_db")  # Output directory for databases
    threads: int = 8  # Number of parallel tasks
    valid_extensions: tuple = (".pdb", ".pdb.gz")  # Supported file types

class FoldseekDBBuilder:
    def __init__(self, config: FoldseekConfig):
        self.config = config
        self.config.db_output_dir.mkdir(parents=True, exist_ok=True)

    def build_all_dbs(self):
        """Main entry: batch create all EC databases"""
        ec_dirs = [d for d in self.config.ec_input_dir.iterdir() 
                  if d.is_dir()]
        
        print(f"Found {len(ec_dirs)} EC directories to process")
        with tqdm(total=len(ec_dirs), desc="Creating databases") as pbar:
            with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
                futures = {executor.submit(self.build_single_db, ec_dir): ec_dir 
                          for ec_dir in ec_dirs}
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        ec_dir = futures[future]
                        print(f"\nError processing {ec_dir.name}: {str(e)}")
                    finally:
                        pbar.update(1)

    def build_single_db(self, ec_dir: Path):
        """Process a single EC directory"""
        # Generate database name (replace dots in EC number with underscores)
        db_name = f"ec_{ec_dir.name.replace('.', '_')}"
        db_path = self.config.db_output_dir / db_name
        
        # Check if database is already complete and doesn't need updating
        if self._check_db_complete(db_path):
            return
        
        # Construct command
        cmd = [
            str(self.config.foldseek_bin),
            "createdb",
            str(ec_dir),
            str(db_path),
            "--threads", "1"  # Run single-threaded per task
        ]
        
        # Execute command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Error handling
        if result.returncode != 0:
            error_msg = (
                f"Creation failed: {ec_dir.name}\n"
                f"Command: {' '.join(cmd)}\n"
                f"Error output: {result.stderr[:500]}"  # Truncate to first 500 chars to avoid overload
            )
            raise RuntimeError(error_msg)
        
        # Log success
        self._write_log(ec_dir, result.stdout, success=True)

    def _is_valid_ec_dir(self, path: Path) -> bool:
        """Validate if it's a valid EC directory"""
        # EC number format validation (e.g.: 1.1.1.1)
        if not re.fullmatch(r"^[\w-]+\.[\w-]+\.[\w-]+\.[\w-]+$", path.name):
            return False
    
        # Contains at least one PDB file
        return any(f.suffix in self.config.valid_extensions for f in path.iterdir())

    def _check_db_complete(self, db_path: Path) -> bool:
        """Check if database files are complete and no update is needed"""
        required_files = [".dbtype", ".index", ".source"]
        return all(db_path.with_suffix(ext).exists() for ext in required_files)

    def _write_log(self, ec_dir: Path, message: str, success: bool):
        """Write to log file"""
        log_file = self.config.db_output_dir / "creation.log"
        with open(log_file, "a") as f:
            status = "SUCCESS" if success else "FAILURE"
            f.write(f"[{status}] {ec_dir.name}\n")
            f.write(f"{'-'*40}\n{message}\n\n")

if __name__ == "__main__":
    config = FoldseekConfig(
        ec_input_dir=Path("./ec_databases"),
        db_output_dir=Path("./ec_create_db")
    )
    
    builder = FoldseekDBBuilder(config)
    builder.build_all_dbs()