import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from prompts import system_prompt
from functions.call_function import available_functions, call_function


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, verbose, user_prompt)


def generate_content(client, messages, verbose, user_prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    if not response.function_calls:
        print(response.text)
        return response.text

    # Collect all function response parts from this turn
    function_response_parts = []
    
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose)
        
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
        
        # Add the function response part to our collection
        function_response_parts.append(function_call_result.parts[0])
    
    # Create a single Content object with all function responses from this turn
    combined_function_response = types.Content(
        role="function",
        parts=function_response_parts
    )
    
    # Add the combined function response to messages for the next iteration
    messages.append(combined_function_response)
    
    # Continue the conversation by calling generate_content recursively
    return generate_content(client, messages, verbose, user_prompt)

if __name__ == "__main__":
    main()
