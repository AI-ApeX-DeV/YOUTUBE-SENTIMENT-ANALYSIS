from flask import Flask, request, render_template, jsonify
import wikipedia
import requests
from bs4 import BeautifulSoup  # Import BeautifulSoup

app = Flask(__name__)

# Wikipedia API settings
wikipedia.set_lang("en")  # Set the language of Wikipedia

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve the user's input from the HTML form
        user_input = request.form.get("user_input")
        
        # Check if the input is a valid Wikipedia page title
        try:
            page = wikipedia.page(user_input)
            page_content = page.content
            page_images = page.images
            page_videos = page.sections[0].videos if page.sections else []

            # Parse the Wikipedia content using BeautifulSoup
            soup = BeautifulSoup(page_content, 'html.parser')

            # Find and format the paragraphs
            formatted_content = ''.join([str(p) for p in soup.find_all('p')])

            return render_template("index.html", content=formatted_content, images=page_images, videos=page_videos)
        except wikipedia.exceptions.PageError:
            result = "Error: Wikipedia page not found."
        
        return render_template("index.html", result=result, content=None, images=None, videos=None)
    
    return render_template("index.html", result=None, content=None, images=None, videos=None)

if __name__ == "__main__":  # Correct the typo here (_ instead of _)
    app.run(debug=True)
