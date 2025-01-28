from flask import Flask, request, render_template_string
import os
from openai import OpenAI
import markdown
from markupsafe import Markup


# client = OpenAI(organization='org-vLZEDXlqppLWrPwAtNgeqk3G')
client = OpenAI()

app = Flask(__name__)

# Set your OpenAI API key
openai_access_key = os.environ['OPENAI_API_KEY']
# openai.api_key = "your-openai-api-key"

# HTML template for the web page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT File Processor</title>
</head>
<body>
    <h1>Upload a Text File</h1>
    <form action="/process" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".txt" required>
        <button type="submit">Submit</button>
    </form>
    {% if response %}
    <h2>ChatGPT Response:</h2>
    <pre>{{ response }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, response=None)

@app.route("/process", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    if file:
        # Read the content of the file
        text = file.read().decode("utf-8")

        sys_prompt = """You are a legal assistant, skilled in explaining 
        complex legal concepts in easy and clear words"""

        # Define a hardcoded prompt
        prompt = f"""Explain in easy words which parts of these terms and
        conditions are harmful or not in the best interest of the user 
        (call them problematic text). Provide line or section or paragraph 
        number as a reference to which text you found harmful.Explain why 
        these are not in the best interest of the user or harmful to the user:
        
        {text}"""

        # Send the text to the ChatGPT API
        try:
            response = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the response text
            # chatgpt_response = response["choices"][0]["message"]["content"]
            response_text = response.choices[0].message.content
            rendered_response = Markup(markdown.markdown(response_text))
        except Exception as e:
            return f"Error communicating with ChatGPT API: {e}", 500

        # Render the template with the response
        return render_template_string(HTML_TEMPLATE, response=rendered_response)

    return "Invalid file", 400

if __name__ == "__main__":
    app.run(debug=True)
