from flask import Flask, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_user_pass(input_path, output_path):
    results = set()

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(":")
            if len(parts) >= 3:
                results.add(f"{parts[1]}:{parts[2]}")

    with open(output_path, "w", encoding="utf-8") as f:
        for item in results:
            f.write(item + "\n")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "No file uploaded"

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(OUTPUT_FOLDER, "result.txt")

        file.save(input_path)
        extract_user_pass(input_path, output_path)

        return send_file(output_path, as_attachment=True)

    return """
    <h2>Upload File</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <br><br>
        <button type="submit">Extract</button>
    </form>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
