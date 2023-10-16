import PyPDF2
import os

def read_file(file_path):
    # Get the file extension
    file_extension = os.path.splitext(file_path)[1]
    
    # Check if the file is a PDF
    if file_extension == '.pdf':
        # Open the PDF file in read-binary mode
        with open(file_path, 'rb') as pdf_file:
            # Create a PdfFileReader object from the opened file
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            # Initialize an empty string variable to store the PDF text
            pdf_text = ''
            # Loop through each page of the PDF file and extract the text
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                pdf_text += page.extractText()
            # Close the opened file
            pdf_file.close()
            # Return the string variable containing the PDF text
            return pdf_text
    # Check if the file is a text file
    elif file_extension == '.txt':
        # Open the text file in read mode
        with open(file_path, 'r') as txt_file:
            # Read the contents of the file
            txt_text = txt_file.read()
            # Close the opened file
            txt_file.close()
            # Return the string variable containing the text
            return txt_text
    # Raise an exception if the file is not a PDF or text file
    else:
        raise Exception('Unsupported file type')
    

