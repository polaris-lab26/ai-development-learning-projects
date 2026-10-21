import re
from flask import Flask, render_template, request

app = Flask(__name__)

# Basic regex pattern for email format validation
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


@app.route("/contact", methods=["GET", "POST"])
def contact():
    errors = {}
    # Retain entered form data on validation failure
    form_data = {"name": "", "email": "", "message": ""}

    if request.method == "POST":
        form_data["name"] = request.form.get("name", "").strip()
        form_data["email"] = request.form.get("email", "").strip()
        form_data["message"] = request.form.get("message", "").strip()

        # Validate Name
        if not form_data["name"]:
            errors["name"] = "Name is required."

        # Validate Email
        if not form_data["email"]:
            errors["email"] = "Email address is required."
        elif not re.match(EMAIL_REGEX, form_data["email"]):
            errors["email"] = "Please enter a valid email address."

        # Validate Message
        if not form_data["message"]:
            errors["message"] = "Message is required."

        # If any validation errors exist, re-render form with 400 Bad Request
        if errors:
            return (
                render_template("contact.html", errors=errors, form_data=form_data),
                400,
            )

        # Success - render confirmation page
        return render_template("success.html", name=form_data["name"])

    # GET request - render initial empty form
    return render_template("contact.html", errors=errors, form_data=form_data)


if __name__ == "__main__":
    app.run(debug=True)
