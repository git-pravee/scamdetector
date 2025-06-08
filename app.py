import re
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from utils.scam_checker import detect_scam
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

app = Flask(__name__)

# Set secret key for session management and flash messages
app.secret_key = os.getenv('SECRET_KEY') or 'fallback_secret_key'  # Always have fallback

# Mail configuration
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# Test mail sending inside app context
with app.app_context():
    try:
        msg = Message("Test Email",
                      recipients=["2ef878f498-7f67c8+user1@inbox.mailtrap.io"])
        msg.body = "This is a test email from ScamShield app using Mailtrap."
        mail.send(msg)
        print("✅ Email sent successfully to Mailtrap inbox.")
    except Exception as e:
        print("❌ Failed to send email:", e)


# Scam keywords regex pattern
SCAM_KEYWORDS = [
    "registration fee", "processing fee", "pay to apply", "money upfront",
    "investment required", "payment", "bank details", "transaction", "fee"
]
scam_pattern = re.compile(
    r'\b(' + '|'.join(re.escape(kw) for kw in SCAM_KEYWORDS) + r')\b', re.IGNORECASE
)

TRUSTED_COMPANIES = [
    "google", "microsoft", "amazon", "facebook", "apple", "intel", "ibm"
]

@app.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        job_title = request.form['job_title'].lower()
        job_desc = request.form['job_description'].lower()
        combined_text = job_title + " " + job_desc

        is_trusted = any(trusted in combined_text for trusted in TRUSTED_COMPANIES)

        if is_trusted:
            flash("✅ <strong>This job looks safe.</strong><br>👍 Still verify company details independently.<br>💼 Apply only through official websites.", "success")
        elif scam_pattern.search(combined_text):
            flash("❌ <strong>Scam Detected!</strong><br>🚫 Never pay for job applications or interviews.<br>🕵️ Research the company before applying.<br>📧 Be cautious with personal information.", "danger")
        else:
            flash("✅ <strong>No scam keywords detected.</strong><br>👍 Still verify company details independently.<br>💼 Apply only through official websites.", "success")

        return redirect(url_for('check'))

    return render_template("check.html")


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        reporter_email = request.form.get("email", "").strip()
        evidence_link = request.form.get("evidence", "").strip()
        scam_details = request.form.get("details", "").strip()

        if not job_title or not reporter_email or not scam_details:
            flash("❌ Please fill in all required fields: Job Title, Email, and Scam Details.", "error")
            return redirect(url_for("report"))

        plain_body = f"""
🚨 Scam Report Submission 🚨

Job Title: {job_title}
Reporter Email: {reporter_email}
Scam Details:
{scam_details}

Evidence Link: {evidence_link if evidence_link else 'None'}

This scam report was submitted via the ScamShield reporting form.
"""

        # Prepare formatted scam details for HTML email
        scam_details_html = scam_details.replace('\n', '<br>')

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{
              font-family: Arial, sans-serif;
              line-height: 1.6;
              color: #333;
              background-color: #f4f4f4;
              padding: 20px;
            }}
            .container {{
              background-color: #ffffff;
              border: 1px solid #ddd;
              border-radius: 8px;
              padding: 20px;
              max-width: 600px;
              margin: auto;
            }}
            h2 {{
              color: #e63946;
            }}
            p {{
              margin: 10px 0;
            }}
            .footer {{
              margin-top: 20px;
              font-size: 0.9em;
              color: #777;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <h2>🚨 Scam Report Submission</h2>
            <p><strong>Job Title:</strong> {job_title}</p>
            <p><strong>Reporter Email:</strong> {reporter_email}</p>
            <p><strong>Scam Details:</strong></p>
            <p>{scam_details_html}</p>
            <p><strong>Evidence Link:</strong> {evidence_link if evidence_link else 'None'}</p>
            <div class="footer">
              <p>This scam report was submitted via the ScamShield reporting form.</p>
            </div>
          </div>
        </body>
        </html>
        """

        try:
            msg = Message(
                subject="🚨 New Scam Report",
                recipients=["2ef878f498-7f67c8+user1@inbox.mailtrap.io"]  # Change as needed
            )
            msg.body = plain_body
            msg.html = html_body
            mail.send(msg)

            flash("✅ Thank you! Your report was successfully submitted.", "success")
        except Exception as e:
            print("Mail send failed:", e)
            flash("❌ Failed to send the report. Please try again later.", "error")

        return redirect(url_for("report"))

    return render_template("report.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        # Format message for HTML
        formatted_message = (message or '').replace('\n', '<br>')

        msg = Message(
            subject=f"ScamShield Contact: {subject}",
            recipients=["2ef878f498-7f67c8+user1@inbox.mailtrap.io"],
            body=f"Name: {name}\nUser Email: {email}\n\nMessage:\n{message}"
        )
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{
              font-family: Arial, sans-serif;
              line-height: 1.6;
              color: #333;
              background-color: #f9f9f9;
              padding: 20px;
            }}
            .container {{
              background-color: #ffffff;
              border: 1px solid #dddddd;
              border-radius: 8px;
              padding: 20px;
              max-width: 600px;
              margin: auto;
            }}
            h2 {{
              color: #2a9d8f;
            }}
            p {{
              margin: 8px 0;
            }}
            .footer {{
              margin-top: 20px;
              font-size: 0.9em;
              color: #777;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <h2>📩 New Contact Message from ScamShield</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong></p>
            <p>{formatted_message}</p>
            <div class="footer">
              <p>This message was sent via the ScamShield contact form.</p>
            </div>
          </div>
        </body>
        </html>
        """

        try:
            mail.send(msg)
            flash("✅ Thank you! Your message has been sent successfully.", "success")
        except Exception as e:
            print("Mail send failed:", e)
            flash("❌ Failed to send your message. Please try again later.", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
