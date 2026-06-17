from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route("/about")
def about():
     return render_template("about.html")


@app.route("/privacy-policy")
def privacy():
     return render_template("privacy.html")


@app.route("/contact")
def contact():
     return render_template("contact.html")

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        image_file = request.files["image"]

        if image_file.filename == "":
            return "Please select image"

        target_kb = int(request.form["target_kb"])

        unique_id = str(uuid.uuid4())

        extension = os.path.splitext(
            image_file.filename
        )[1]

        upload_path = os.path.join(
            UPLOAD_FOLDER,
            unique_id + extension
        )

        image_file.save(upload_path)

        original_size = (
            os.path.getsize(upload_path)
            / 1024
        )

        img = Image.open(upload_path)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        compressed_path = os.path.join(
            COMPRESSED_FOLDER,
            unique_id + ".jpg"
        )

        quality = 95

        while quality >= 10:

            img.save(
                compressed_path,
                "JPEG",
                optimize=True,
                quality=quality
            )

            compressed_size = (
                os.path.getsize(compressed_path)
                / 1024
            )

            if compressed_size <= target_kb:
                break

            quality -= 5

        saved_percent = round(
            (
                (original_size - compressed_size)
                / original_size
            ) * 100,
            1
        )

        return render_template(
            "result.html",
            original_size=round(original_size, 2),
            compressed_size=round(compressed_size, 2),
            saved_percent=saved_percent,
            file_id=unique_id
        )

    return render_template("index.html")


@app.route("/download/<file_id>")
def download(file_id):

    path = os.path.join(
        COMPRESSED_FOLDER,
        file_id + ".jpg"
    )

    return send_file(
        path,
        as_attachment=True,
        download_name="compressed.jpg"
    )
    

if __name__ == "__main__":
    app.run(debug=True)




