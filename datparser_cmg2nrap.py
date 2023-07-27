import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


def extract_year_from_line(line):
    # Use regular expression to find the year in the last set of brackets '()'
    # match = re.search(r'\((\d{4})', line)
    match = re.search(r'\((.*?)\)', line)
    if match:
        return match.group(1)
    return None


def process_chunk(year, data_lines, output_file, write_headers=False):
    # Step 5: Save the processed data into a new .dat file
    mode = 'a' if not write_headers else 'w'
    with open(output_file, mode) as outfile:
        if write_headers:
            outfile.write("Year\ti_index\tj_index\tk_index\tx_coord m\ty_coord m\tz_coord m\tGas_Saturation\n")  # Write header line
        for line in data_lines:
            processed_line = f"{year}\t{line}"  # Append the 'year' to the beginning of the line
            outfile.write(processed_line + '\n')


def process_large_dat_file(input_file, output_file):
    # Step 1: Read the file and process each block
    data_lines = []
    year = None
    write_headers = True

    with open(input_file, 'r') as infile:
        for line_number, line in enumerate(infile):
            if line.startswith("CMG Results"):
                # If we encounter a new block, process the previous block first
                if year and data_lines:
                    # Skip the first two rows (header lines) for subsequent blocks
                    process_chunk(year, data_lines[8:], output_file, write_headers)
                    data_lines.clear()
                    write_headers = False  # No need to write headers for subsequent blocks

                # Extract the year from the line
                year = extract_year_from_line(line)
            else:
                data_lines.append(line.strip())

        # Process the last remaining block
        if year and data_lines:
            process_chunk(year, data_lines[8:], output_file, write_headers)


def process_large_dat_files(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".gslib"):
            input_file = os.path.join(input_folder, filename)
            output_folder = os.path.join(input_folder, "output")  # Create an "output" folder within the input folder
            os.makedirs(output_folder, exist_ok=True)

            output_file = os.path.join(output_folder, filename[:-6] + "_nrap.dat")
            process_large_dat_file(input_file, output_file)


def select_input_folder():
    input_folder = filedialog.askdirectory(title="Select Input Folder")
    if input_folder:
        process_large_dat_files(input_folder)
        print("Processing complete. Check the 'output' folder within the input folder.")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    select_input_folder()
