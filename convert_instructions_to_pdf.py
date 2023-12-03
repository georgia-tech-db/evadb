import os
import subprocess
from pathlib import Path

DOC_ROOT_DIR = "docs/source/"

def convert_rst_to_pdf(rst_file_lst, output_path):

    for i,rst_file in enumerate(rst_file_lst):

        try:
            # Run rst2pdf command using subprocess
            file_name = rst_file.split("/")[-1]
            file_name = file_name[:-4]

            if not Path(output_path+file_name+".pdf").is_file():
                output_file = output_path+file_name+".pdf"

                subprocess.run(['rst2pdf', rst_file, '-o', output_file], check=True)
                print(f"Conversion successful. PDF saved to {output_path+file_name}")
        
        except subprocess.CalledProcessError as e:
            print(f"Conversion failed. Error: {e}")

        if i%10 == 0:
            print(f"Completed {i} files")

        



def get_all_files_recursively(directory):
    directory_path = Path(directory)
    all_files = list(directory_path.rglob('*'))
    return all_files


def convert_instr_to_pdf():

    all_files_in_directory = get_all_files_recursively(DOC_ROOT_DIR)
    all_files_in_directory = [str(f) for f in all_files_in_directory]
    all_files_in_directory = [f for f in all_files_in_directory if f.endswith(".rst")]

    print(f"TOtal nos of files: {len(all_files_in_directory)}")

    os.mkdir("doc_pdf/")
    convert_rst_to_pdf(all_files_in_directory, 'doc_pdf/')


