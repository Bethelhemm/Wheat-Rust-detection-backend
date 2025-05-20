import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing API key: {api_key[:10]}...")

genai.configure(api_key=api_key)

# List available models
try:
    # Try using the standard model
    model = genai.GenerativeModel()
    print("Successfully configured model")
    
    # Try a simple request
    response = model.generate_content("Hello, how are you?")
    print("\nResponse:")
    print(response.text)
except Exception as e:
    print(f"\nError: {str(e)}")
