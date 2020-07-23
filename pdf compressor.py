# This script uses ghostscript to compress pdf files
# Please ensure that you have ghostscript before running
#You can either give a file path or a directory path

import os
import glob
import subprocess


def start(path, quality):
    pdf_quality = pdf_quality_to_cmd(quality)
    if os.path.isdir(path):
        process_directory(path, pdf_quality)
    elif os.path.isfile(path):
        process_file(path, pdf_quality)


def pdf_quality_to_cmd(in_quality):
    if in_quality == 'h':
        return '/prepress'
    elif in_quality == 'm':
        return '/ebook'
    else:
        return '/screen'


def process_directory(dir_path, pdf_quality):
    pdf_list = glob.glob(dir_path + "*.pdf")
    os.makedirs(dir_path + "Compressed", exist_ok=True)
    compressed_path = dir_path + 'Compressed/'

    for pdf in pdf_list:
        pdf_name = pdf.replace(dir_path, "")
        subprocess.run(['gs', '-dBATCH', '-dNOPAUSE', f'-dPDFSETTINGS={pdf_quality}', '-sDEVICE=pdfwrite',
                        f'-sOUTPUTFILE={compressed_path + pdf_name}', f'{pdf}'])


def process_file(file_path, pdf_quality):
    pdf_name = os.path.basename(file_path)
    compressed_pdf_name = 'compressed' + pdf_name
    modified_file_path = file_path.replace(pdf_name, "")
    subprocess.run(['gs', '-dBATCH', '-dNOPAUSE', f'-dPDFSETTINGS={pdf_quality}', '-sDEVICE=pdfwrite',
                    f'-sOUTPUTFILE={modified_file_path + compressed_pdf_name}', f'{file_path}'])


if __name__ == '__main__':
    from shutil import which

    if which('gs') is not None:
        input_pdf_path = str(input("Enter the path of pdf: "))

        input_quality = str(input(
            "Select a quality:\n" +
            "1. High (Higher quality output (300 dpi) but bigger size)(H or h)\n" +
            "2. Medium (Medium quality output (150 dpi) with moderate output file size) (M or m)\n" +
            "3. Low (Lower quality output (72 dpi) but smallest possible output file size) (L or l)\n" +
            "Enter input: ")).lower()

        while input_quality not in ('h', 'm', 'l'):
            input_quality = str(input("Please enter (H or M or L) according to quality:")).lower()

        start(input_pdf_path, input_quality)

    else:
        print("Please visit the website to install ghostscript.\nhttps://www.ghostscript.com/doc/current/Install.htm")
