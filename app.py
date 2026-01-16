from flask import Flask, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_file(input_path, output_path, remove_duplicates, email_to_user):
    results = []

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(":")
            if len(parts) < 2:
                continue

            # case: link:user:pass
            if len(parts) >= 3:
                user = parts[1]
                password = parts[2]
            else:
                user = parts[0]
                password = parts[1]

            # email -> user
            if email_to_user and "@" in user:
                user = user.split("@")[0]

            results.append(f"{user}:{password}")

    if remove_duplicates:
        results = list(set(results))

    with open(output_path, "w", encoding="utf-8") as f:
        for item in results:
            f.write(item + "\n")


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
        body {
            background:#f4f6f8;
            font-family: Arial;
        }
        .box {
            width:400px;
            margin:80px auto;
            background:white;
            padding:25px;
            border-radius:8px;
            box-shadow:0 0 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align:center;
        }
        button {
            width:100%;
            padding:10px;
            background:#007bff;
            color:white;
            border:none;
            border-radius:5px;
            cursor:pointer;
        }
        button:hover {
            background:#0056b3;
        }
    </style>
</head>
<body>
    <div class="box">
        <h2>User:Pass Extractor</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required><br><br>

            <label>
                <input type="checkbox" name="remove_duplicates" checked>
                Remove Duplicates
            </label><br><br>

            <label>
                <input type="checkbox" name="email_to_user">
                Convert Email → User
            </label><br><br>

            <button type="submit">Process & Download</button>
        </form>
    </div>
</body>
</html>
"""


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
