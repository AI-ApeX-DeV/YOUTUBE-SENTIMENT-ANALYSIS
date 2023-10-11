from flask import Flask, request, render_template
import wikipedia

app = Flask(__name__)

# Wikipedia API settings
wikipedia.set_lang("en")  # Set the language of Wikipedia

@app.route("/", methods=["GET", "POST"])
def index():
    content = None
    images = None
    videos = None

    if request.method == "POST":
        # Retrieve the user's input from the HTML form
        user_input = request.form.get("user_input")

        try:
            # Try to retrieve Wikipedia page content
            page = wikipedia.page(user_input)
            content = page.content
            images = page.images

            # Check if the page has sections with videos
            if page.sections:
                videos = []
                for section in page.sections:
                    if section.videos:
                        videos.extend(section.videos)

        except wikipedia.exceptions.PageError:
            result = "Error: Wikipedia page not found."

    return render_template("index.html", content=content, images=images, videos=videos)

if __name__ == "__main__":
    app.run(debug=True)
