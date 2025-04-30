import subprocess
import os
import sys
import time
from pathlib import Path

def run_notebook(notebook_path):
    """Execute a notebook via command line with proper path handling for spaces"""
    print(f"\n{'='*50}")
    print(f"Executing: {os.path.basename(notebook_path)}")
    print(f"Full path: {notebook_path}")
    print(f"{'='*50}\n")

    # Check if file exists first
    if not os.path.exists(notebook_path):
        print(f"ERROR: Notebook not found at {notebook_path}")
        return False

    start_time = time.time()
    # Quote the path to handle spaces properly
    quoted_path = f'"{notebook_path}"'
    cmd = f"jupyter nbconvert --execute --to notebook --inplace {quoted_path}"

    print(f"Running command: {cmd}")
    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"Error executing {notebook_path}")
        return False

    elapsed = time.time() - start_time
    print(f"\nCompleted: {os.path.basename(notebook_path)} in {elapsed:.2f} seconds")
    return True

def main():
    # Get the path to the PROJECT root (up one level from package)
    package_dir = Path(__file__).parent
    project_root = package_dir.parent
    notebooks_dir = project_root / "notebooks"

    print(f"Package directory: {package_dir}")
    print(f"Project root: {project_root}")
    print(f"Notebooks directory: {notebooks_dir}")

    if not notebooks_dir.exists():
        print(f"ERROR: Notebooks directory not found at {notebooks_dir}")
        sys.exit(1)

    # Define notebook paths with proper Path objects
    notebooks = [
        notebooks_dir / "transcript_collection.ipynb",
        notebooks_dir / "data_cleaning.ipynb",
        notebooks_dir / "enhanced_sentiment.ipynb",
        notebooks_dir / "data_visualization.ipynb", 
        notebooks_dir / "sec_8k_analysis.ipynb",  # Adjusted filename based on what we saw earlier
        notebooks_dir / "summary_visualizations.ipynb"
    ]

    # Run each notebook in sequence
    success = True
    for notebook in notebooks:
        if not run_notebook(str(notebook)):
            success = False
            print(f"WARNING: Failed to run {notebook}")
            # Continue with next notebook rather than exiting

    if success:
        print("\nEntire pipeline executed successfully!")
    else:
        print("\nPipeline completed with some errors. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
