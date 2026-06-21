import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# ---- Firebase Admin SDK ----
cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---- Flask-Mail ----
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)

EMAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT')


# ========================
#       PUBLIC ROUTES
# ========================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/In-depth-Pricing-Packages.html')
def package_docs():
    return render_template('In-depth-Pricing-Packages.html')

@app.route('/Process.html')
def process():
    return render_template('Process.html')

@app.route('/send-inquiry', methods=['POST'])
def send_inquiry():
    data = request.form
    try:
        msg = Message(
            subject=f"New Inquiry from {data.get('name', 'Unknown')}",
            recipients=[EMAIL_RECIPIENT],
            body=f"""
Selected Package: {data.get('selected_package', 'N/A')}
Name: {data.get('name', '')}
Email: {data.get('email', '')}
Phone: {data.get('phone', '')}
App Type: {data.get('app_type', '')}
Domain Type: {data.get('domain_type', '')}
Custom Domain: {data.get('custom_domain', 'N/A')}
Hosting Type: {data.get('hosting_type', '')}

Specifications:
{data.get('specs', '')}
            """
        )
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Thank you! We will get back to you shortly.'})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Failed to send email. Please try again later.'}), 500
    
@app.route('/submit-review', methods=['POST'])
def submit_review():
    data = request.json
    name = data.get('name')
    rating = data.get('rating')
    review = data.get('review')
    website = data.get('website', '')

    if not name or not rating or not review:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        db.collection('reviews').add({
            'reviewer': name,
            'rating': int(rating),
            'review': review,
            'website': website,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({'success': True, 'message': 'Thank you for your review!'})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Failed to save review'}), 500


if __name__ == '__main__':
    app.run(debug=True)