# Fast Fee - WhatsApp School Fees Payment Bot (Flask + Twilio)

from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Mock student database
students_db = {}
# Simple in-memory session store
sessions = {}

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    sender = request.form.get('From')
    msg = request.form.get('Body').strip()
    print(f"\n[Webhook hit] From: {sender}, Message: {msg}")  # DEBUG

    response = MessagingResponse()
    session = sessions.get(sender, {"stage": 0})
    print(f"[Current session] {session}")  # DEBUG

    if session["stage"] == 0:
        response.message("Hello, how are you? How can I help you today?\n\n1. Pay School Fees")
        session["stage"] = 1
        print("[Stage 0] Greeted user")  # DEBUG

    elif session["stage"] == 1:
        if msg == "1":
            response.message("Please enter the Student's Full Name:")
            session["stage"] = 2
            print("[Stage 1] User chose to pay fees")  # DEBUG
        else:
            response.message("Invalid option. Please type 1 to continue.")
            print("[Stage 1] Invalid input")  # DEBUG

    elif session["stage"] == 2:
        session["student_name"] = msg
        response.message("Enter the School Name:")
        session["stage"] = 3
        print(f"[Stage 2] Collected name: {msg}")  # DEBUG

    elif session["stage"] == 3:
        session["school_name"] = msg
        response.message("Enter the Bank Account Number:")
        session["stage"] = 4
        print(f"[Stage 3] School name: {msg}")  # DEBUG

    elif session["stage"] == 4:
        session["bank_account"] = msg
        response.message("Which payment method do you want to use?\n1. Ecocash\n2. PayPal\n3. Other")
        session["stage"] = 5
        print(f"[Stage 4] Bank account: {msg}")  # DEBUG

    elif session["stage"] == 5:
        if msg == "1":
            session["payment_method"] = "Ecocash"
            response.message("Enter your Ecocash Number:")
            session["stage"] = 6
            print("[Stage 5] Chose Ecocash")  # DEBUG
        elif msg == "2":
            session["payment_method"] = "PayPal"
            response.message("Please visit this link to pay via PayPal: https://paypal.com/pay/fastfee")
            response.message("Once completed, reply with 'done'.")
            session["stage"] = 8
            print("[Stage 5] Chose PayPal")  # DEBUG
        elif msg == "3":
            session["payment_method"] = "Other"
            response.message("Please specify your preferred method (e.g. Visa, Mastercard):")
            session["stage"] = 7
            print("[Stage 5] Chose Other")  # DEBUG
        else:
            response.message("Invalid option. Please choose 1, 2, or 3.")
            print("[Stage 5] Invalid input")  # DEBUG

    elif session["stage"] == 6:
        session["ecocash_number"] = msg
        response.message("Enter your Ecocash PIN:")
        session["stage"] = 9
        print(f"[Stage 6] Ecocash number: {msg}")  # DEBUG

    elif session["stage"] == 7:
        session["payment_method"] = msg
        response.message(f"Please follow this link to pay with {msg}: https://paymentgateway.com/fastfee")
        response.message("Once completed, reply with 'done'.")
        session["stage"] = 8
        print(f"[Stage 7] Other method: {msg}")  # DEBUG

    elif session["stage"] == 8:
        if msg.lower() == "done":
            response.message("Payment confirmed! Generating your receipt...")
            receipt = f"""
Payment Receipt - Fast Fee
--------------------------
Student: {session.get('student_name')}
School: {session.get('school_name')}
Bank Account: {session.get('bank_account')}
Payment Method: {session.get('payment_method')}
Status: Paid
"""
            response.message(receipt + "\n\nYou may screenshot this and send it to the school as proof of payment.")
            print("[Stage 8] Payment marked as done. Sending receipt")  # DEBUG
            sessions[sender] = {"stage": 0}
        else:
            response.message("Please type 'done' after completing your payment.")
            print("[Stage 8] Waiting for 'done'")  # DEBUG

    elif session["stage"] == 9:
        session["ecocash_pin"] = msg
        response.message("Processing payment via Ecocash...")
        response.message("Payment successful! Generating your receipt...")
        receipt = f"""
Payment Receipt - Fast Fee
--------------------------
Student: {session.get('student_name')}
School: {session.get('school_name')}
Bank Account: {session.get('bank_account')}
Payment Method: Ecocash
Ecocash Number: {session.get('ecocash_number')}
Status: Paid
"""
        response.message(receipt + "\n\nYou may screenshot this and send it to the school as proof of payment.")
        print("[Stage 9] Ecocash payment processed. Receipt sent")  # DEBUG
        sessions[sender] = {"stage": 0}

    sessions[sender] = session
    print(f"[Updated session] {session}")  # DEBUG
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
