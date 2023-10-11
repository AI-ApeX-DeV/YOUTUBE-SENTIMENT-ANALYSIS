from flask import Flask, request, render_template, Response
import wikipedia
from fpdf import FPDF

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
            content = page.content[:500]  # Limit the content to the first 500 characters
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

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    content = request.form.get("content")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    response = Response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=wikipedia_content.pdf'
    return response

if __name__ == "__main__":
    app.run(debug=True)
