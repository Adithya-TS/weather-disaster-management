"""
Quick test script to send a test email alert.
This bypasses subscriptions and sends directly to your email.
"""

import requests
import sys

# Configuration
API_URL = "http://localhost:8000"
YOUR_EMAIL = "prasathram387@gmail.com"  # CHANGE THIS to your email
YOUR_TOKEN = ""  # Will try to get from response or use provided one

def get_test_token():
    """Try to login and get a token (you'll need to implement proper auth)"""
    # For now, you need to login via web UI and copy the token
    print("⚠️  You need to be logged in to send test emails")
    print("1. Go to http://localhost:3000")
    print("2. Login with Google")
    print("3. Open browser console (F12)")
    print("4. Run: localStorage.getItem('token')")
    print("5. Copy the token and paste it here")
    print()
    token = input("Paste your JWT token here: ").strip()
    return token

def send_test_email(email: str, token: str):
    """Send a test email alert"""
    
    if not token:
        print("❌ No token provided. Cannot send test email.")
        return False
    
    url = f"{API_URL}/alerts/test-email"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "email": email,
        "location": "Test Location - Jaffna"
    }
    
    print(f"\n📧 Sending test email to: {email}")
    print(f"🌐 API URL: {url}")
    print("⏳ Please wait...\n")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            if result.get("success"):
                print("✅ SUCCESS! Test email sent successfully!")
                print(f"📬 {result.get('message', '')}")
                print(f"\n💡 Check your inbox: {email}")
                print("   (Don't forget to check spam folder too!)")
                return True
            else:
                print("❌ Email sending failed!")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
                if "help" in result:
                    print("\n📚 Help:")
                    help_info = result["help"]
                    if isinstance(help_info, dict):
                        for key, value in help_info.items():
                            print(f"\n{key}:")
                            if isinstance(value, list):
                                for item in value:
                                    print(f"  - {item}")
                            else:
                                print(f"  {value}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {result}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure backend is running: uvicorn src.api.fastapi_app:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_URL}/healthz", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
    except:
        pass
    
    print("❌ Backend is NOT running!")
    print("   Start it with: uvicorn src.api.fastapi_app:app --reload")
    return False

def main():
    print("="*60)
    print("📧 EMAIL ALERT TEST TOOL")
    print("="*60)
    print()
    
    # Check backend
    if not check_backend():
        return
    
    # Get email address
    print(f"\n📬 Current email: {YOUR_EMAIL}")
    change = input("Change email address? (y/n): ").strip().lower()
    if change == 'y':
        email = input("Enter your email: ").strip()
    else:
        email = YOUR_EMAIL
    
    if not email or '@' not in email:
        print("❌ Invalid email address!")
        return
    
    # Get token
    if not YOUR_TOKEN:
        token = get_test_token()
    else:
        token = YOUR_TOKEN
    
    if not token:
        return
    
    # Send test email
    success = send_test_email(email, token)
    
    if success:
        print("\n" + "="*60)
        print("🎉 EMAIL TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📝 Next Steps:")
        print("1. Check your inbox for the test alert email")
        print("2. If no email, check spam/junk folder")
        print("3. If still no email, check SMTP configuration in .env")
        print("\n📖 For SMTP setup, see: EMAIL_SETUP_TESTING_GUIDE.md")
    else:
        print("\n" + "="*60)
        print("❌ EMAIL TEST FAILED")
        print("="*60)
        print("\n📝 Troubleshooting:")
        print("1. Check if SMTP_USER and SMTP_PASSWORD are set in .env")
        print("2. For Gmail, use App Password (not regular password)")
        print("3. Restart backend after changing .env")
        print("\n📖 See detailed guide: EMAIL_SETUP_TESTING_GUIDE.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(0)

