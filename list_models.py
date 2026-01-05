import os
from google import genai

def list_models():
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        # The new SDK might typically expose this via client.models.list() 
        # or similar. Let's try the standard iteration.
        
        print("Listing available models...")
        # Note: In the new google-genai SDK, listing might differ from google-generativeai.
        # We will try the common access pattern.
        # If this fails, we'll see the error and adjust.
        
        pager = client.models.list() 
        for model in pager:
            print(f"Model: {model.name}")
            print(f"  DisplayName: {model.display_name}")
            print(f"  SupportedGenerationMethods: {model.supported_generation_methods}")
            print("-" * 20)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_models()
