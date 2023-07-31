import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

def extract_info_within_parentheses(line):
    # Use regular expression to find the content within the parentheses '()'
    match = re.search(r'\((.*?)\)', line)
    if match:
        return match.group(1)
    return None


def process_chunk(info_within_parentheses, property, data_lines, output_file, write_headers=False):
    # Step 5: Save the processed data into a new .dat file
    mode = 'a' if not write_headers else 'w'
    with open(output_file, mode) as outfile:
        if write_headers:
            last_header = property.split('\t')[-1]  # Extract the last header from the data_lines list of the first chunk
            header_line = f"Year i_index j_index k_index x_coord_m y_coord_m z_coord_m {last_header}\n"
            outfile.write(header_line)  # Write header line with the last header from the first chunk
        for line in data_lines:
            processed_line = info_within_parentheses + " " + line.replace('\t', ' ')  # Replace tabs with spaces
            outfile.write(processed_line + '\n')


def process_large_dat_file(input_file, output_file, progress_var):
    try:
        # Step 1: Read the file and process each block
        data_lines = []
        year = None
        write_headers = True

        with open(input_file, 'r') as infile:
            total_lines = sum(1 for _ in infile)  # Get the total number of lines in the input file
            infile.seek(0)  # Reset the file pointer to the beginning
            processed_lines = 0

            for line_number, line in enumerate(infile):
                if line.startswith("CMG Results"):
                    # If we encounter a new block, process the previous block first
                    if year and data_lines:
                        # Skip the first two rows (header lines) for subsequent blocks
                        process_chunk(year, data_lines[7], data_lines[8:], output_file, write_headers)
                        data_lines.clear()
                        write_headers = False  # No need to write headers for subsequent blocks

                    # Extract the year from the line
                    year = extract_info_within_parentheses(line)
                else:
                    data_lines.append(line.strip())

                # Update the progress bar
                processed_lines += 1
                progress_var.set(int(processed_lines / total_lines * 100))
                root.update_idletasks()

            # Process the last remaining block
            if year and data_lines:
                process_chunk(year, data_lines[7], data_lines[8:], output_file, write_headers)

        messagebox.showinfo("Processing Complete", f"File {input_file} processed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing {input_file}:\n{str(e)}")


def process_large_dat_files(input_files):
    for input_file in input_files:
        if input_file.endswith(".gslib"):
            input_folder = os.path.dirname(input_file)
            output_folder = os.path.join(input_folder, "output")  # Set the output folder to 'output' under the input folder
            os.makedirs(output_folder, exist_ok=True)

            output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + "_nrap.txt")

            # Create a progress bar
            progress_var = tk.DoubleVar()
            progress_bar = Progressbar(root, variable=progress_var, maximum=100)
            progress_bar.pack(fill=tk.X, padx=5, pady=5)

            process_large_dat_file(input_file, output_file, progress_var)

            progress_bar.destroy()


def select_input_files():
    input_files = filedialog.askopenfilenames(
        title="Select Input Files",
        filetypes=[("GSlib Files", "*.gslib")]
    )
    if input_files:
        process_large_dat_files(input_files)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    select_input_files()
