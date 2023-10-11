from flask import Flask, request, render_template, Response
import wikipedia
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch  # Add this import

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

    return render_template("index2.html", content=content, images=images, videos=videos)

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    content = request.form.get("content")
    images = request.form.getlist("images")

    response = generate_pdf(content, images)
    return response

def generate_pdf(content, images):
    response = Response(content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=wikipedia_ebook.pdf'

    # Create a PDF document
    buffer = response.stream
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Set font and margin
    c.setFont("Helvetica", 12)
    top_margin = 0.75 * inch
    left_margin = 0.75 * inch
    text_width = width - 2 * left_margin

    # Split content into paragraphs
    paragraphs = content.split("\n")
    for paragraph in paragraphs:
        # Calculate remaining space on the page
        remaining_space = height - c._y

        # If there's not enough space for the paragraph, add a new page
        if remaining_space < 1 * inch:
            c.showPage()
            c.setFont("Helvetica", 12)

        # Draw the paragraph
        c.drawString(left_margin, height - c._y, paragraph)
        c._y += 16

    # Add images to the PDF
    for image_url in images:
        c.showPage()
        c.drawImage(image_url, left_margin, top_margin, width - 2 * left_margin, height - 2 * top_margin, preserveAspectRatio=True)

    c.save()
    buffer.seek(0)
    response.set_data(buffer.read())
    return response

if __name__ == "__main__":
    app.run(debug=True)
