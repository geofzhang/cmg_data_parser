import os
import tkinter as tk
from tkinter import filedialog, messagebox

def process_chunk(year, header_lines, data_lines, output_file):
    # Step 3: Create column headers using rows 2 to 9
    columns = header_lines[1:9]

    # Step 4: Insert the 'year' into column 1 for every row
    processed_data = []
    for line in data_lines:
        processed_data.append(year + '\t' + line)  # Assuming tab-separated values

    # Step 5: Save the processed data into a new .dat file
    if os.path.exists(output_file):
        overwrite = messagebox.askyesno("File Exists", f"Do you want to overwrite {output_file}?")
        if not overwrite:
            print(f"Skipping processing for {output_file}")
            return

    with open(output_file, 'w') as outfile:
        outfile.write('\t'.join(['Year'] + columns) + '\n')  # Write header line
        outfile.write('\n'.join(processed_data) + '\n')


def process_large_dat_file(input_file, output_file):
    # Step 1: Read the file in chunks
    chunk_size = 10000  # Number of lines to read in each chunk
    header_lines = []
    data_lines = []
    year = None  # Initialize year to None

    with open(input_file, 'r') as infile:
        for line_number, line in enumerate(infile):
            if line_number == 0:
                year = line.strip()[-11:-7]  # Extract year from the first line
                continue  # Skip processing row 1

            if 1 <= line_number <= 9:
                header_lines.append(line.strip())
            else:
                data_lines.append(line.strip())

            if line_number % chunk_size == 0:
                # Step 2: Process the current chunk
                process_chunk(year, header_lines, data_lines, output_file)
                header_lines.clear()
                data_lines.clear()

        # Process the last remaining chunk
        process_chunk(year, header_lines, data_lines, output_file)


def process_large_dat_files(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".dat"):
            input_file = os.path.join(input_folder, filename)
            output_folder = os.path.join(input_folder, "output")  # Create an "output" folder within the input folder
            os.makedirs(output_folder, exist_ok=True)

            output_file = os.path.join(output_folder, filename[:-4] + "_nrap.dat")
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
