from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    # Read the content of conclusion.txt
    with open('conclusion.txt', 'r') as file:
        conclusion_text = file.read()

    # HTML template with dynamic content insertion
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Design Comparison Result</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 20px;
                background-color: #f4f4f4;
            }
            h1 {
                color: #4CAF50;
            }
            p {
                font-size: 16px;
                color: #555;
            }
            pre {
                background-color: #def4d6;
                padding: 15px;
                border-radius: 5px;
                font-size: 14px;
                line-height: 1.6;
                color: #333;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <h1>Design Comparison Result</h1>
        <p>
            The comparison between the designs has been processed. The results and suggestions on which design is better are as follows:
        </p>
        <pre>
            {{ conclusion_text }}
        </pre>
    </body>
    </html>

    """

    # Render the HTML with the conclusion text
    return render_template_string(html_content, conclusion_text=conclusion_text)

if __name__ == '__main__':
    app.run(debug=True, port=9090) 