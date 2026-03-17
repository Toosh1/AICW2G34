import os
import re
from pathlib import Path

def clean_filename(filename):
    """Remove numbers, months, 'issue', 'Station Disruption Plan', and symbols from filename."""
    # Remove file extension
    name, ext = os.path.splitext(filename)
    
    # Remove numbers
    name = re.sub(r'\d+', '', name)
    
    # Remove month names (case-insensitive)
    months = r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b'
    name = re.sub(months, '', name, flags=re.IGNORECASE)
    
    # Remove 'issue' (case-insensitive)
    name = re.sub(r'\bissue\b', '', name, flags=re.IGNORECASE)
    
    # Remove 'Station Disruption Plan' (case-insensitive)
    name = re.sub(r'\bstation\s+disruption\s+plan\b', '', name, flags=re.IGNORECASE)
    
    # Remove symbols, keep only alphanumeric and spaces
    name = re.sub(r'[^a-zA-Z\s]', '', name)
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    # Restore extension
    return f"{name}{ext}"

def rename_docx_files():
    """Rename all DOCX files in current directory."""
    directory = Path(__file__).parent
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.docx'):
            old_path = directory / filename
            new_filename = clean_filename(filename)
            new_path = directory / new_filename
            
            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} → {new_filename}")

# Example usage
if __name__ == "__main__":
    rename_docx_files()