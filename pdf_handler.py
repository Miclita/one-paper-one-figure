"""
PDF Handler Module
Handles PDF file upload and extraction
"""
import PyPDF2
import os
import base64


def read_pdf_content(file_path):
    """
    Read and extract text content from PDF file
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content from PDF
    """
    content = ""
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
                
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")
        
    return content


def encode_pdf_to_base64(file_path):
    """
    Encode PDF file to base64 string for uploading
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Base64 encoded string of the PDF file
    """
    try:
        with open(file_path, 'rb') as file:
            encoded_pdf = base64.b64encode(file.read()).decode('utf-8')
        return encoded_pdf
    except Exception as e:
        raise Exception(f"Error encoding PDF file: {str(e)}")


def get_pdf_info(file_path):
    """
    Get basic information about the PDF file
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing PDF information
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            info = {
                'pages': len(pdf_reader.pages),
                'file_size': os.path.getsize(file_path)
            }
            
            # Get metadata if available
            metadata = pdf_reader.metadata
            if metadata:
                info['title'] = metadata.get('/Title', 'Unknown')
                info['author'] = metadata.get('/Author', 'Unknown')
                
        return info
    except Exception as e:
        raise Exception(f"Error getting PDF information: {str(e)}")