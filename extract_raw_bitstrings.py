import json
import base64
import zlib
import struct
import sys
import os

def extract_raw_bitstrings(result_file_path, output_file=None):
    """Extract all raw bitstrings from the job result without headers or delimiters."""
    # Load the job result
    with open(result_file_path, 'r') as f:
        result_data = json.load(f)
    
    # Navigate to the BitArray data
    try:
        # Get all field data
        fields = result_data['__value__']['pub_results'][0]['__value__']['data']['__value__']['fields']
        
        # Collect all bitstrings in order
        all_bitstrings = []
        
        # Process each register in order
        for register in ['c_central', 'c_inner', 'c_middle', 'c_outer']:
            if register in fields:
                bit_array_data = fields[register]['__value__']
                array_data = bit_array_data['array']['__value__']
                num_bits = bit_array_data['num_bits']
                
                # Decode the base64 data
                decoded_data = base64.b64decode(array_data)
                
                # Decompress the data
                decompressed_data = zlib.decompress(decoded_data)
                
                # Convert to integers
                fmt = f"{len(decompressed_data)//8}Q"  # 8-byte unsigned long long
                unpacked_data = struct.unpack(fmt, decompressed_data)
                
                # Convert to bitstrings
                bitstrings = [format(val, f'0{num_bits}b') for val in unpacked_data]
                all_bitstrings.extend(bitstrings)
        
        # Join all bitstrings into one continuous string
        full_bitstring = ''.join(all_bitstrings)
        
        # Write to output file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(full_bitstring)
        
        return full_bitstring
    except Exception as e:
        print(f"Error extracting bitstrings: {e}")
        return None

def process_directory(directory_path, output_dir=None):
    """Process all result files in a directory.
    
    Args:
        directory_path: Path to directory containing result files
        output_dir: Directory to save raw bitstrings (default: directory_path/raw_bitstrings)
    """
    from pathlib import Path
    
    directory_path = Path(directory_path)
    if output_dir is None:
        output_dir = directory_path / 'raw_bitstrings'
    else:
        output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all result files
    result_files = list(directory_path.glob('job-*-result.json'))
    print(f"Found {len(result_files)} result files")
    
    # Process each result file
    for result_file in result_files:
        print(f"\nProcessing {result_file.name}...")
        try:
            # Extract job ID from filename
            job_id = result_file.stem.split('-')[1]
            
            # Set output file path
            output_file = output_dir / f"raw_bitstring_{job_id}.txt"
            
            # Extract bitstrings
            full_bitstring = extract_raw_bitstrings(result_file, output_file)
            
            if full_bitstring:
                print(f"Extracted {len(full_bitstring)} bits")
                print(f"Saved to {output_file}")
        except Exception as e:
            print(f"Error processing {result_file.name}: {e}")

def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Extract raw bitstrings from quantum job results")
    parser.add_argument("--directory", required=True, help="Directory containing job result files")
    parser.add_argument("--output", help="Output directory for raw bitstrings")
    args = parser.parse_args()
    
    # Process all files in the directory
    process_directory(args.directory, args.output)

if __name__ == "__main__":
    main()
