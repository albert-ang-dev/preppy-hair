from http.server import BaseHTTPRequestHandler
import json
import os
import resend

# Initialize Resend with the environment variable
resend.api_key = os.environ.get("RESEND_API_KEY")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read the length of the data and parse the JSON body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode('utf-8'))
        
        # 2. Extract values from frontend form
        user_email = body.get("email")
        user_name = body.get("name")
        user_message = body.get("message")
        barber_id = body.get("barberId")
        client_appt_id = body.get("clientApptId")

        try:
            # 3. Fire the email via Resend
            params = {
                "from": "send@preppyhair.site", # Your verified sender email
                "to": [user_email], # Where you want to receive notifications
                "subject": f"Walk-In  {user_name}",
                "html": f"""
                    <h3>PREPPY HAIR</h3>
                    <p>Congratulations you are now checked in!</p>
                    <p>Please see your waitlist position.</p>
                    <p><a href="https://preppyhair.site/waitlist/{barber_id}?customerId={client_appt_id}">View Waitlist Position</a></p>
                """
            }
            
            email_response = resend.Emails.send(params)
            
            # 4. Return successful response to Nuxt
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {"success": True, "message": "Email sent!", "id": email_response.get("id")}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            # Handle backend errors safely
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_data = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
