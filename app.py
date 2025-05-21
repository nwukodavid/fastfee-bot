from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Mock student database
students_db = {}

# Simple in-memory session store
sessions = {}

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    sender = request.form.get('From')
    msg = request.form.get('Body').strip()
    print(f"\n[Webhook hit] From: {sender}, Msg: {msg}")

    response = MessagingResponse()

    # Handle "restart" command
    if msg.lower() == "restart":
        sessions[sender] = {"stage": 0}
        response.message(
            "Session restarted. Welcome to Fast Fee!\n"
            "How can I help you today?\n"
            "1. Pay School Fees\n"
            "2. Check Payment Status\n"
            "3. Other"
        )
        return str(response)

    session = sessions.get(sender, {"stage": 0})
    print(f"[Current session] {session}")

    if session["stage"] == 0:
        response.message(
            "Hello, how are you?\n"
            "1. Pay School Fees\n"
            "2. Check Payment Status\n"
            "3. Other"
        )
        session["stage"] = 1
        print("[Stage 0] Greeted user")

    elif session["stage"] == 1:
        if msg == "1":
            response.message("Enter your Ecocash Number:")
            session["stage"] = 2
            print("[Stage 1] User chose to pay school fees")
        elif msg == "2":
            response.message("Please enter your payment reference number.")
            session["stage"] = 5  # Example stage for checking payment
            print("[Stage 1] User checking payment")
        else:
            response.message("Invalid option. Please reply with 1, 2, or 3.")

    elif session["stage"] == 2:
        session["ecocash_number"] = msg
        response.message("Enter your Ecocash PIN:")
        session["stage"] = 3
        print("[Stage 2] Collected Ecocash number")

    elif session["stage"] == 3:
        session["ecocash_pin"] = msg
        response.message("Processing payment via Ecocash...")
        print("[Stage 3] Collected PIN and processing payment")

        # Simulated payment processing
        receipt_text = (
            "Payment Receipt - Fast Fee\n"
            "--------------------------\n"
            "Student: Nwuko\n"
            "School: Futo\n"
            f"Bank Account: {session['ecocash_number']}\n"
            "Payment Method: Ecocash\n"
            f"Ecocash Number: {session['ecocash_number']}\n"
            "Status: Paid\n\n"
            "You may screenshot this and send it to the school as proof of payment."
        )
        response.message("Payment successful! Generating your receipt…")
        response.message(receipt_text)

        # Clear session
        sessions.pop(sender, None)
        print("[Stage 3] Payment complete, session reset")

    else:
        response.message("Sorry, something went wrong. Please type 'restart' to start over.")
        print("[Unknown stage] User session in unknown state")

    sessions[sender] = session  # Save session
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
