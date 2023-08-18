import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

def extract_info_within_parentheses(line):
    # Use regular expression to find the content within the parentheses '()'
    match = re.search(r'\((.*?)\)', line)
    if match:
        return match.group(1)
    return None

def format_year(year_str):
    # A mapping of month abbreviations to their respective numbers
    month_map = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }

    year, month, day = year_str.split('-')
    return f"{year}{month_map[month]}{day}"

def format_property(header):
    if header == 'Gas_Saturation':
        formatted_header = 'CO2_Sat'
    elif header == 'Pres_drop_from_time_zero':
        formatted_header = 'Pres_drop'
    else:
        formatted_header = header
    return formatted_header

def process_chunk(year, property, data_lines, output_file, write_headers=False, filter_k_values=None):
    # Step 5: Save the processed data into a new .dat file
    mode = 'a' if not write_headers else 'w'
    with open(output_file, mode) as outfile:
        if write_headers:
            last_header_line = property.split('\t')[-1]  # Extract the last header from the data_lines list of the first chunk
            last_header = format_property(last_header_line.split()[0])
            header_line = f"Year i j k x y z {last_header}\n"
            outfile.write(header_line)  # Write header line with the last header from the first chunk
        for line in data_lines:
            parts = line.split()
            if filter_k_values and parts[2] not in filter_k_values:  # Assuming k is the 3rd column in your data
                continue
            formatted_year = format_year(year)  # Reformat year from the CMG output to: YYYYMMDD
            processed_line = formatted_year + " " + line.replace('\t', ' ')  # Replace tabs with spaces
            outfile.write(processed_line + '\n')


def process_large_dat_file(input_file, output_file, progress_var, filter_k=None):
    try:
        # Step 1: Read the file and process each block
        data_lines = []
        year = None
        write_headers = True
        UPDATE_FREQUENCY = 500000

        with open(input_file, 'r') as infile:
            total_lines = sum(1 for _ in infile)  # Get the total number of lines in the input file
            infile.seek(0)  # Reset the file pointer to the beginning
            processed_lines = 0

            for line_number, line in enumerate(infile):
                if line.startswith("CMG Results"):
                    # If we encounter a new block, process the previous block first
                    if year and data_lines:
                        # Skip the first two rows (header lines) for subsequent blocks
                        process_chunk(year, data_lines[7], data_lines[8:], output_file, write_headers, filter_k)
                        data_lines.clear()
                        write_headers = False  # No need to write headers for subsequent blocks

                    # Extract the year from the line
                    year = extract_info_within_parentheses(line)
                else:
                    data_lines.append(line.strip())

                # Update the progress bar
                processed_lines += 1
                if processed_lines % UPDATE_FREQUENCY == 0:
                    progress_var.set(int(processed_lines / total_lines * 100))
                    root.update_idletasks()

            # Process the last remaining block
            if year and data_lines:
                process_chunk(year, data_lines[7], data_lines[8:], output_file, write_headers, filter_k)


            # Update one last time at the end to ensure it reaches 100%
            progress_var.set(100)
            root.update_idletasks()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing {input_file}:\n{str(e)}")


def process_large_dat_files(input_files):
    filter_k_values = [k.strip() for k in k_var.get().split(',')]
    print(filter_k_values)
    for input_file in input_files:
        if input_file.endswith(".gslib"):
            input_folder = os.path.dirname(input_file)
            output_folder = os.path.join(input_folder, "output")  # Set the output folder to 'output' under the input folder
            os.makedirs(output_folder, exist_ok=True)
            file_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_folder, file_name + "_nrap.txt")

            # Create a progress bar
            progress_var = tk.DoubleVar()
            progress_bar = Progressbar(root, variable=progress_var, maximum=100)
            progress_bar.pack(fill=tk.X, padx=5, pady=5)

            process_large_dat_file(input_file, output_file, progress_var, filter_k_values)

            progress_bar.destroy()
    root.after(0, show_completion_message())

def show_completion_message():
    messagebox.showinfo("Processing Complete", f"Files processed successfully!")

def load_input_files():
    input_files = filedialog.askopenfilenames(
        title="Select Input Files",
        filetypes=[("GSlib Files", "*.gslib")]
    )
    if input_files:
        threading.Thread(target=process_large_dat_files, args=(input_files,)).start()


def select_input_files():
    load_button = tk.Button(root, text="Load .gslib files", command=load_input_files)
    load_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title('CMG Data Parser')
    root.geometry("300x200")

    status_var = tk.StringVar()
    status_var.set("Waiting for files to be processed...")
    status_label = tk.Label(root, textvariable=status_var)
    status_label.pack(pady=20)

    k_var = tk.StringVar()
    k_label = tk.Label(root, text="Enter k values (use ',' to separate):")
    k_label.pack(pady=5)
    k_entry = tk.Entry(root, textvariable=k_var)
    k_entry.pack(pady=5)

    select_input_files()
