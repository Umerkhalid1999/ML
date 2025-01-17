from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None  # Initialize the result
    if request.method == "POST":
        try:
            # Get input values from the form
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operation = request.form["operation"]

            # Perform the selected operation
            if operation == "add":
                result = num1 + num2
            elif operation == "subtract":
                result = num1 - num2
            elif operation == "multiply":
                result = num1 * num2
            elif operation == "divide":
                if num2 != 0:
                    result = num1 / num2
                else:
                    result = "Error: Division by zero is not allowed."
            else:
                result = "Invalid operation selected."
        except ValueError:
            result = "Error: Invalid input. Please enter valid numbers."

    return render_template("calculator.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
