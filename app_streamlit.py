import openai
import streamlit as st
from streamlit_ace import st_ace
import subprocess
import os
import black

# OpenAI API key
import os
api_key = os.getenv("OPENAI_API_KEY")
#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
# Supported languages
languages = {
    "Python": "py",
    "C++": "cpp",
    "Java": "java"
}

# Function to format code for each language
def format_code(code, language):
    if language == "Python":
        # Apply black formatting for Python code
        try:
            formatted_code = black.format_str(code, mode=black.FileMode())
            return formatted_code
        except Exception as e:
            st.error(f"Python formatting error: {e}")
            return code
    elif language in ["C++", "Java"]:
        # Simple indentation rule for C++ and Java
        formatted_code = "\n".join(line.strip() for line in code.splitlines())
        return formatted_code
    else:
        return code

# Streamlit app
st.title("AI Code Compiler & Assistant")

# Sidebar - Language Selection
st.sidebar.header("Select Language")
language = st.sidebar.selectbox("Choose a programming language", list(languages.keys()))

# Ace editor for code input
st.subheader(f"Write your {language} code below:")

# Set the mode for Ace based on the selected language
language_mode = {
    "Python": "python",
    "C++": "c_cpp",
    "Java": "java"
}
code_input = st_ace(
    language=language_mode[language],
    theme="monokai",
    height=300,
    key="code_editor",
    value=""  # Initial value can be set here if needed
)

# Code formatting
if st.button("Format Code"):
    formatted_code = format_code(code_input, language)
    st_ace(
        language=language_mode[language],
        theme="monokai",
        height=300,
        key="formatted_editor",
        value=formatted_code  # Corrected from initial_value to value
    )

# AI Suggestion (OpenAI Codex)
if st.button("Get AI Suggestion"):
    if code_input.strip():
        try:
            response = openai.Completion.create(
                engine="davinci-codex",
                prompt=code_input,
                max_tokens=150,
                temperature=0.5
            )
            suggestion = response.choices[0].text.strip()
            st_ace(
                language=language_mode[language],
                theme="monokai",
                height=300,
                key="suggestion_editor",
                value=suggestion  # Corrected from initial_value to value
            )
        except Exception as e:
            st.error(f"Error with AI Suggestion: {e}")
    else:
        st.warning("Please enter some code or a prompt to get AI suggestions.")

# Code execution (compilation and running)
if st.button("Run Code"):
    if code_input.strip():
        file_extension = languages[language]
        file_name = f"temp_code.{file_extension}"
        
        # Save code to file
        with open(file_name, "w") as file:
            file.write(code_input)
        
        # Run the code based on language selection
        if language == "Python":
            result = subprocess.run(["python", file_name], capture_output=True, text=True)
        elif language == "C++":
            subprocess.run(["g++", file_name, "-o", "output"], capture_output=True, text=True)
            result = subprocess.run(["./output"], capture_output=True, text=True)
        elif language == "Java":
            subprocess.run(["javac", file_name], capture_output=True, text=True)
            result = subprocess.run(["java", file_name.replace(".java", "")], capture_output=True, text=True)
        
        # Display the output
        if result.returncode == 0:
            st.subheader("Output:")
            st.code(result.stdout)
        else:
            st.error(f"Error in execution:\n{result.stderr}")

        # Clean up
        if os.path.exists(file_name):
            os.remove(file_name)
        if os.path.exists("output"):
            os.remove("output")
    else:
        st.warning("Please write some code before running it.")

# Code download option
if st.button("Download Code"):
    if code_input.strip():
        file_extension = languages[language]
        file_name = f"code.{file_extension}"

        # Write the code to the file
        with open(file_name, "w") as file:
            file.write(code_input)

        # Provide a download link
        with open(file_name, "rb") as file:
            st.download_button(f"Download {file_name}", file, file_name)

        # Clean up
        if os.path.exists(file_name):
            os.remove(file_name)
    else:
        st.warning("Please write some code before downloading it.")
