"""
LLM Client Module
Handles communication with various LLM APIs including Gemini and Nano-Banana
"""
import openai
from config import API_KEY, BASE_URL, MODEL_NAME, NANO_BANANA_MODEL
import base64


class LLMClient:
    def __init__(self, api_key=None, base_url=None):
        """
        Initialize the LLM client
        
        Args:
            api_key (str): API key for the service
            base_url (str): Base URL for the API
        """
        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        
    def send_pdf_to_llm(self, pdf_content, prompt, model_name=None):
        """
        Send PDF content and prompt to LLM
        
        Args:
            pdf_content (str): Content of the PDF file
            prompt (str): Prompt to send to the LLM
            model_name (str): Name of the model to use
            
        Returns:
            str: Response from the LLM
        """
        model = model_name or MODEL_NAME
        
        try:
            # Combine prompt with PDF content
            full_prompt = f"{prompt}\n\nPDF Content:\n{pdf_content}"
            
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error communicating with LLM: {str(e)}")
            
    def send_image_request_to_nanobanana(self, image_prompt, model_name=None):
        """
        Send image generation request to Nano-Banana
        
        Args:
            image_prompt (str): Prompt for image generation
            model_name (str): Name of the model to use
            
        Returns:
            str: Response from Nano-Banana
        """
        model = model_name or NANO_BANANA_MODEL
        
        try:
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": image_prompt}
                ]
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error communicating with Nano-Banana: {str(e)}")

    def send_messages_to_llm(self, messages, model_name=None):
        """
        Send custom messages to LLM
        
        Args:
            messages (list): List of message dictionaries
            model_name (str): Name of the model to use
            
        Returns:
            str: Response from the LLM
        """
        model = model_name or MODEL_NAME
        
        try:
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error communicating with LLM: {str(e)}")