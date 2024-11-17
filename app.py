# Necessary imports
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from http import HTTPStatus

# Local imports
from src.services.content_cleaner import clean_content
from src.services.jina_reader import fetch_data
from src.logger import logging


# Load environment variables
load_dotenv()

# Instantiating flask app
application = Flask(__name__)
app = application
CORS(app)


# Home route for the app
@app.route("/")
def main():
    return render_template("home.html")


# Generate response endpoint
@app.route("/generate", methods=["POST"])
def generate():
    """
    Endpoint to generate a response for a given web article URL.

    Expected JSON body:
    {
        "url": "Your web article URL",
    }
    """
    # Validate request body
    data = request.get_json()

    if not data or "url" not in data:
        return (
            jsonify(
                {
                    "error": "Missing web article 'url' in request body",
                    "status": "error",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        # Get the prompt from request
        reader_llm_response = fetch_data(data["url"], os.environ.get("JINA_API_KEY"))

        # Generate response
        response = clean_content(reader_llm_response)

        # Log successful response
        logging.info("Response generated successfully for prompt")

        # Return response
        return jsonify({"status": "success", "response": response}), HTTPStatus.OK

    # Handle exceptions
    except Exception as e:
        logging.error(f"Error in converting to text: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": "Oops! Something went wrong. Please try again later.",
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# Driver code for running the app
if __name__ == "__main__":
    app.run(debug=True)
