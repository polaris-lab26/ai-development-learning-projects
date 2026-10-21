import re

from flask import Flask, render_template, request

app = Flask(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html", errors=[], form={})

    form = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "message": request.form.get("message", "").strip(),
    }

    errors = []
    if not form["name"]:
        errors.append("Name is required.")
    if not form["email"]:
        errors.append("Email is required.")
    elif not EMAIL_RE.match(form["email"]):
        errors.append("Email address is not valid.")
    if not form["message"]:
        errors.append("Message is required.")

    if errors:
        return render_template("contact.html", errors=errors, form=form), 400

    return render_template("confirmation.html", name=form["name"])


if __name__ == "__main__":
    app.run(debug=True)