from flask import Flask, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_file(input_path, output_path, remove_duplicates, email_to_user):
    seen = set() if remove_duplicates else None

    with open(input_path, "r", encoding="utf-8", errors="ignore") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:

        for line in infile:
            line = line.strip()
            if not line:
                continue

            parts = line.split(":")
            if len(parts) < 2:
                continue

            # link:user:pass
            if len(parts) >= 3:
                user = parts[1]
                password = parts[2]
            else:
                user = parts[0]
                password = parts[1]

            # email -> user
            if email_to_user and "@" in user:
                user = user.split("@", 1)[0]

            result = f"{user}:{password}"

            if remove_duplicates:
                if result in seen:
                    continue
                seen.add(result)

            outfile.write(result + "\n")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "No file uploaded"

        remove_duplicates = request.form.get("remove_duplicates") == "on"
        email_to_user = request.form.get("email_to_user") == "on"

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(OUTPUT_FOLDER, "result.txt")

        file.save(input_path)

        process_file(
            input_path,
            output_path,
            remove_duplicates,
            email_to_user
        )

        return send_file(output_path, as_attachment=True)

    return """
<!DOCTYPE html>
<html>
<head>
<title>Extractor Tool</title>
<style>
body{background:#f4f6f8;font-family:Arial}
.box{width:420px;margin:80px auto;background:#fff;padding:25px;
border-radius:8px;box-shadow:0 0 10px rgba(0,0,0,.1)}
button{width:100%;padding:10px;background:#007bff;color:#fff;
border:none;border-radius:5px}
</style>
</head>
<body>
<div class="box">
<h2>User:Pass Extractor</h2>
<form method="POST" enctype="multipart/form-data">
<input type="file" name="file" required><br><br>

<label>
<input type="checkbox" name="remove_duplicates" checked>
Remove Duplicates (RAM heavy)
</label><br><br>

<label>
<input type="checkbox" name="email_to_user">
Email → User
</label><br><br>

<button type="submit">Process & Download</button>
</form>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
