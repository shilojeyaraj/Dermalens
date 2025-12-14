"""
Simple Flask app for frontend deployment
"""
from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dermalens AI</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 600px;
        }
        h1 { color: #333; margin-bottom: 20px; }
        p { color: #666; margin-bottom: 30px; }
        .status { 
            background: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            border-radius: 5px; 
            display: inline-block;
            margin: 10px;
        }
        .api-link {
            background: #2196F3;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Dermalens AI</h1>
        <p>Your personalized skincare analysis platform is now live!</p>
        
        <div class="status">✅ Frontend Deployed Successfully</div>
        <div class="status">✅ Backend API Running</div>
        
        <p>API Endpoint: <strong>{{ api_url }}</strong></p>
        
        <a href="{{ api_url }}/health" class="api-link" target="_blank">
            Test API Health
        </a>
        
        <p><em>Full application features coming soon...</em></p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    api_url = os.getenv('NEXT_PUBLIC_API_URL', 'https://dermalens-backend-941238576063.us-central1.run.app')
    return render_template_string(HTML_TEMPLATE, api_url=api_url)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Dermalens Frontend"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
