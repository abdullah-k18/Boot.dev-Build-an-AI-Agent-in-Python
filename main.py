import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file

load_dotenv()

if len(sys.argv) < 2:
    print("Error: Prompt is required", file=sys.stderr)
    sys.exit(1)

prompt = sys.argv[1]
verbose = "--verbose" in sys.argv

api_key = os.getenv("GEMINI_API_KEY")

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = {
    "name": "get_files_info",
    "description": "Lists files in the specified directory along with their sizes, constrained to the working directory.",
    "parameters": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            },
        },
        "required": [],
    },
}

schema_get_file_content = {
    "name": "get_file_content",
    "description": "Reads and returns the contents of a specified file, constrained to the working directory.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read, relative to the working directory.",
            },
        },
        "required": ["file_path"],
    },
}

schema_run_python_file = {
    "name": "run_python_file",
    "description": "Executes a Python file with optional arguments, constrained to the working directory.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the Python file to execute, relative to the working directory.",
            },
        },
        "required": ["file_path"],
    },
}

schema_write_file = {
    "name": "write_file",
    "description": "Writes or overwrites content to a specified file, constrained to the working directory.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to write to, relative to the working directory.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file.",
            },
        },
        "required": ["file_path", "content"],
    },
}

available_functions = [
    {
        "function_declarations": [
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file
        ]
    }
]

client = genai.Client(api_key=api_key)

def call_function(function_call_part, verbose=False):
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }
    function_name = function_call_part.name
    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    try:
        function_result = function_map[function_name](**args)
    except Exception as e:
        function_result = f"Exception: {e}"
    part = types.Part.from_function_response(
        name=function_name,
        response={"content": function_result},
    )
    print(f"[DEBUG] Function response part: {part}")
    return types.Content(
        role="tool",
        parts=[part],
    )

messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
max_iterations = 20
iteration = 0

while iteration < max_iterations:
    print(f"[DEBUG] Messages before generate_content:")
    for m in messages:
        print(m)
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config={
            "tools": available_functions,
            "system_instruction": system_prompt
        }
    )
    if hasattr(response, 'function_calls') and response.function_calls:
        for candidate in response.candidates:
            messages.append(candidate.content)
        function_response_parts = []
        print(f"[DEBUG] Function call parts:")
        for fc in response.function_calls:
            print(fc)
        print(f"[DEBUG] Number of function calls: {len(response.function_calls)}")
        for function_call_part in response.function_calls:
            function_call_result = call_function(function_call_part, verbose=verbose)
            function_response_parts.extend(function_call_result.parts)
        print(f"[DEBUG] Number of function response parts: {len(function_response_parts)}")
        messages.append(types.Content(role="tool", parts=function_response_parts))
        iteration += 1
    else:
        for candidate in response.candidates:
            candidate_text = None
            if candidate.content and candidate.content.parts:
                part = candidate.content.parts[0]
                if hasattr(part, 'text') and part.text:
                    candidate_text = part.text
            if candidate_text:
                messages.append(types.Content(role="model", parts=[types.Part(text=candidate_text)]))
        break

if iteration >= max_iterations:
    print("Warning: Maximum iterations reached. The agent may not have completed its task.")
