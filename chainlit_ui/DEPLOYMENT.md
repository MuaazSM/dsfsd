# Deployment Guide for Real Estate Multilingual Chatbot

This guide explains how to deploy the chatbot on Chainlit Cloud and set up the necessary services.

## Prerequisites

- OpenAI API key
- Firebase project with Firestore enabled
- Google Cloud account for Speech-to-Text (optional)
- Twilio account for voice integration (optional)
- Chainlit Cloud account or Hugging Face Spaces account

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/real-estate-chatbot.git
cd real-estate-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables by creating a `.env` file based on the provided template.

## Local Testing

1. Start the chatbot locally:
```bash
python main.py
```

2. Start the admin dashboard:
```bash
python main.py --mode admin
```

3. Run the test suite:
```bash
pytest
```

## Deploying to Chainlit Cloud

1. Create a Chainlit account at [https://chainlit.io](https://chainlit.io)

2. Install the Chainlit CLI:
```bash
pip install chainlit-cli
```

3. Login to Chainlit:
```bash
chainlit login
```

4. Deploy the application:
```bash
chainlit deploy
```

5. Configure environment variables in the Chainlit Cloud console:
   - Add your OpenAI API key
   - Add your Firebase service account credentials
   - Add other optional API keys

6. Enable any required permissions and services in the Chainlit Cloud console.

## Deploying to Hugging Face Spaces

1. Create a Hugging Face account at [https://huggingface.co](https://huggingface.co)

2. Create a new Space:
   - Select "Chainlit" as the SDK
   - Choose Python version 3.9+

3. Upload your code to the Space:
   - You can use Git or the Hugging Face web interface
   - Make sure to include all required files:
     - `.env.example` (renamed to `.env`)
     - `requirements.txt`
     - `chainlit.md`
     - All Python files

4. Configure environment variables in the Space settings:
   - Add your OpenAI API key as `OPENAI_API_KEY`
   - Add your Firebase service account JSON as `FIREBASE_SERVICE_ACCOUNT_KEY`
   - Add other required API keys

5. Set the Spaces environment to run the application:
   - Set the entry point to `main.py`

## Firestore Database Setup

1. Create a Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com)

2. Enable Firestore Database in your project:
   - Go to "Firestore Database" in the Firebase console
   - Click "Create database"
   - Choose "Start in production mode" or "Start in test mode" (for development)
   - Select a location for your database

3. Create service account credentials:
   - Go to "Project settings" > "Service accounts"
   - Click "Generate new private key"
   - Save the JSON file
   - Use the content of this file for the `FIREBASE_SERVICE_ACCOUNT_KEY` environment variable

4. Set up Firestore security rules:
   - Go to "Firestore Database" > "Rules"
   - Configure appropriate security rules for your application
   - Example rules:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

## Google Cloud Speech-to-Text Setup (Optional)

1. Create a Google Cloud project at [https://console.cloud.google.com](https://console.cloud.google.com)

2. Enable the Speech-to-Text API:
   - Go to "APIs & Services" > "Library"
   - Search for "Speech-to-Text API"
   - Click "Enable"

3. Create service account credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create credentials" > "Service account key"
   - Create a new service account or select an existing one
   - Download the JSON key file
   - Use the same Firebase service account key or create a dedicated one

## Twilio Voice Integration Setup (Optional)

1. Create a Twilio account at [https://www.twilio.com](https://www.twilio.com)

2. Get your Twilio credentials:
   - Account SID
   - Auth Token
   - Twilio phone number

3. Configure your webhook URL:
   - Once your application is deployed, set up a webhook URL in Twilio
   - Use the URL: `https://your-app-url.com/twilio/webhook`
   - Set the webhook method to POST

4. Add Twilio credentials to your environment variables:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

## Monitoring and Maintenance

1. Chainlit Cloud provides built-in monitoring tools:
   - View conversation logs
   - Track API usage
   - Monitor performance metrics

2. For database monitoring:
   - Use Firebase Console to monitor Firestore usage
   - Set up Firebase alerts for quota limits

3. Regular maintenance:
   - Update dependencies regularly
   - Monitor API usage costs
   - Back up conversation data periodically

## Troubleshooting

1. If the application fails to start:
   - Check environment variables
   - Verify API keys are valid
   - Check logs for specific error messages

2. If language detection or translation is not working:
   - Verify OpenAI API key is valid
   - Check API rate limits
   - Verify connectivity to OpenAI services

3. If database operations fail:
   - Check Firebase service account credentials
   - Verify Firestore security rules
   - Check quota and billing status

4. For deployment issues:
   - Check Chainlit documentation for specific deployment errors
   - Verify that all dependencies are properly installed
   - Check for version conflicts in requirements.txt