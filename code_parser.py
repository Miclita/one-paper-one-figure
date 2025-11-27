"""
Code Parser Module
Parses code blocks from LLM responses
"""
import re


def extract_code_blocks(text):
    """
    Extract code blocks from text response
    
    Args:
        text (str): Text containing code blocks
        
    Returns:
        list: List of extracted code blocks
    """
    # Pattern to match code blocks enclosed in triple backticks
    pattern = r"```(?:\w+)?\s*\n(.*?)\n\s*```"
    
    # Find all matches
    code_blocks = re.findall(pattern, text, re.DOTALL)
    
    # Clean up each code block
    cleaned_blocks = []
    for block in code_blocks:
        # Remove leading/trailing whitespace from each line
        cleaned_block = '\n'.join(line.rstrip() for line in block.split('\n'))
        # Remove leading/trailing empty lines
        cleaned_block = cleaned_block.strip()
        cleaned_blocks.append(cleaned_block)
        
    return cleaned_blocks


def extract_last_code_block(text):
    """
    Extract the last code block from text response
    
    Args:
        text (str): Text containing code blocks
        
    Returns:
        str: Last code block, or None if no code blocks found
    """
    code_blocks = extract_code_blocks(text)
    
    if code_blocks:
        return code_blocks[-1]
    
    return None


def extract_python_code_blocks(text):
    """
    Extract Python code blocks specifically
    
    Args:
        text (str): Text containing code blocks
        
    Returns:
        list: List of extracted Python code blocks
    """
    # Pattern to match Python code blocks
    pattern = r"```(?:python|py)\s*\n(.*?)\n\s*```"
    
    # Find all matches
    code_blocks = re.findall(pattern, text, re.DOTALL)
    
    # Clean up each code block
    cleaned_blocks = []
    for block in code_blocks:
        # Remove leading/trailing whitespace from each line
        cleaned_block = '\n'.join(line.rstrip() for line in block.split('\n'))
        # Remove leading/trailing empty lines
        cleaned_block = cleaned_block.strip()
        cleaned_blocks.append(cleaned_block)
        
    # If no Python-specific blocks found, try general code blocks
    if not cleaned_blocks:
        cleaned_blocks = extract_code_blocks(text)
        
    return cleaned_blocks


def extract_last_python_code_block(text):
    """
    Extract the last Python code block from text response
    
    Args:
        text (str): Text containing code blocks
        
    Returns:
        str: Last Python code block, or None if no code blocks found
    """
    code_blocks = extract_python_code_blocks(text)
    
    if code_blocks:
        return code_blocks[-1]
    
    return None