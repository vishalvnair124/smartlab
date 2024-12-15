import json
from customtkinter import *
from PIL import Image
import uuid
import requests



# Initialize Application
app = CTk()
app.geometry("600x480")
app.iconbitmap("./attendance.ico")
app.title("SmartLab")

invalid_var = BooleanVar(value=False)
global invalid_text 
invalid_text = "Invalid credintial"

# Load Images
side_img_data = Image.open("side-img.png")
email_icon_data = Image.open("email-icon.png")
password_icon_data = Image.open("password-icon.png")
session_icon_data = Image.open("session.png")

side_img = CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))
email_icon = CTkImage(dark_image=email_icon_data, light_image=email_icon_data, size=(20, 20))
password_icon = CTkImage(dark_image=password_icon_data, light_image=password_icon_data, size=(17, 17))
session_icon = CTkImage(dark_image=session_icon_data, light_image=session_icon_data, size=(17, 17))

def get_mac_address():
    try:
        mac_address = hex(uuid.getnode()).replace("0x", "").zfill(12)
        formatted_mac = ":".join(mac_address[i:i+2] for i in range(0, len(mac_address), 2))
        return formatted_mac
    except Exception as e:
        return f"Error: {e}"

def send_login(email, password, session_id):
    global invalid_text
    # Step 1: Get the MAC address of the device
    mac_address = get_mac_address()

    # Step 2: Define the server URL (replace with your Flask server URL)
    url = "http://127.0.0.1:5000/slogin"  # Update with your actual server URL

    # Step 3: Prepare the request payload
    payload = {
        "email": email,
        "password": password,
        "session": session_id,
        "mac_address": mac_address
    }

    try:
        # Step 4: Send POST request to the server
        response = requests.post(url, json=payload)

        # Step 5: Check the response status code and handle the result
        if response.status_code == 200:
            respons = response.json()
            print("Login successful!")
            print(f"Name: {respons['name']}")
            print(f"Email: {respons['email']}")
            print(f"Session Ends At: {respons['session_end']}")
            return respons
        elif response.status_code == 401:
            print("Invalid credentials or inactive student.")
            invalid_text = "Invalid credentials"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
        elif response.status_code == 403:
            print("Unauthorized device or inactive device.")
            invalid_text = "Unauthorized device"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
        elif response.status_code == 404:
            print("Invalid or inactive session.")
            invalid_text = "Invalid  session"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
        else:
            print("An error occurred:", response.json().get('message', 'Unknown error'))
            invalid_text = "Unknown error"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
    except requests.exceptions.RequestException as e:
        print(f"Failed to send request: {e}")

    # If unsuccessful, return a failure response
    return {
        "response": 500,
        "message": "Login failed due to an error."
    }




def send_logout(response_from):
    mac_address = get_mac_address()
    
    try:
        # API Endpoint for Logout
        logout_url = "http://127.0.0.1:5000/slogout"  
        response_from.update({"mac_address": mac_address})
        # print(response_from)
        # Send POST request with response_from data
        response = requests.post(logout_url, json=response_from)
        # print("test2")
        # Check server response
        if response.status_code == 200:
            print("Logout Successful")
            return response.json()  # Return the response JSON from the server
        else:
            print(f"Logout Failed: {response.status_code}")
            return response.json()  # Return error details from the server's response

    except requests.exceptions.RequestException as e:
        print(f"Error sending logout request: {e}")
        return {
            "response": 500,
            "message": "Failed to send logout request"
        }



def device_registration(email, password):
    global invalid_text
    mac_add = get_mac_address()  # Assuming this function fetches the MAC address
    print(f"Sending registration for {email} with MAC address: {mac_add}")
    
    # Prepare data to be sent in the POST request
    data = {
        'email': email,
        'password': password,
        'mac_address': mac_add
    }
    
    try:
        # Send a POST request with the email, password, and MAC address as JSON data
        response = requests.post("http://127.0.0.1:5000/device_registration", json=data)
        
        # Log the response from the server for debugging purposes
        print(f"Server response: {response.text}")
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return response.json()  # Return the JSON response if successful
        elif response.status_code == 500:
            print(f"Failed with status code {response.status_code}")
            invalid_text = "Already Registered!"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
            return {"response": response.status_code, "message": response.text}
        elif response.status_code == 404:
            print(f"Failed with status code {response.status_code}")
            invalid_text = "Invalid credintial"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
            return {"response": response.status_code, "message": response.text}    
        else:
            print(f"Failed with status code {response.status_code}")
            invalid_text = "Registration Failed!"  # Update invalid text
            invalid_var.set(True)  # Trigger UI update
            return {"response": response.status_code, "message": response.text}
    except requests.exceptions.RequestException as e:
        # This will catch any network-related errors, such as connection timeouts, etc.
        invalid_text = "Registration Failed!"  # Update invalid text
        invalid_var.set(True)  # Trigger UI update
        print(f"Error making the request: {e}")
        return {"response": 500, "message": f"Request exception: {str(e)}"}
    
    except Exception as e:
        # This will catch any other exceptions
        print(f"Unexpected error: {e}")
        invalid_text = f"Unexpected error: {str(e)}"  # Update invalid text
        invalid_var.set(True)  # Trigger UI update
        return {"response": 500, "message": f"Unexpected error: {str(e)}"}




# Function to Replace the Right Frame
def on_login_click(email_entry, password_entry, session_entry):
    email = email_entry.get()  # Get the email value from the entry widget
    password = password_entry.get()  # Get the password value from the entry widget
    session = session_entry.get()  # Get the session value from the entry widget
    
    if session == "000000" :
       response = device_registration(email,password)
       if response["response"] == 200:
           display_registred()
       else:
           invalid_var.set(True)
           display_login_form()
    else:
        response = send_login(email, password, session)
        if response["response"] == 200:
            display_logedin(response)
        else:
            display_login_form()

def display_registred():
    for widget in right_panel.winfo_children():
        widget.destroy()
    CTkLabel(
            master=right_panel,
            text="Dashboard",
            font=("Arial Bold", 24),
            text_color="#601E88"
        ).pack(pady=50)

    CTkLabel(
            master=right_panel,
            text="Device Registred",
            font=("Arial", 16),
            text_color="#601E88",
            anchor="center"
        ).pack(pady=10)
    
def logout(response_from):
    
    response = send_logout(response_from)
    if response["response"] == 200:
        for widget in right_panel.winfo_children():
            widget.destroy()
        display_login_form()

def display_logedin(response):
    for widget in right_panel.winfo_children():
        widget.destroy()
    CTkLabel(
            master=right_panel,
            text="Dashboard",
            font=("Arial Bold", 24),
            text_color="#601E88"
        ).pack(pady=50)
    CTkLabel(
            master=right_panel,
            text=f"Welcome {response["name"]}!".format(),
            font=("Arial", 16),
            text_color="#601E88",
            anchor="center"
        ).pack(pady=10)
    CTkButton(
            master=right_panel,
            text="Logout",
            fg_color="#E44982",
            hover_color="#601E88",
            text_color="white",
            command= lambda :logout(response)
        ).pack(pady=20)

def display_login_form():
    # Create entry widgets and store them locally
    for widget in right_panel.winfo_children():
        widget.destroy()
    email_entry = CTkEntry(master=right_panel, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
    password_entry = CTkEntry(master=right_panel, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000", show="*")
    session_entry = CTkEntry(master=right_panel, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
    
    CTkLabel(master=right_panel, text="Welcome Back!", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))

    CTkLabel(master=right_panel, text="  Email", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=email_icon, compound="left").pack(anchor="w", pady=(38, 0), padx=(25, 0))
    email_entry.pack(anchor="w", padx=(25, 0))

    CTkLabel(master=right_panel, text="  Password", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=password_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
    password_entry.pack(anchor="w", padx=(25, 0))

    CTkLabel(master=right_panel, text="  Session", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=session_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
    session_entry.pack(anchor="w", padx=(25, 0))

    CTkButton(
        master=right_panel,
        text="Login",
        fg_color="#601E88",
        hover_color="#E44982",
        font=("Arial Bold", 12),
        text_color="#ffffff",
        width=225,
        command=lambda: on_login_click(email_entry, password_entry, session_entry)  # Use lambda to pass the entry widgets
    ).pack(anchor="w", pady=(40, 0), padx=(25, 0))

    label = CTkLabel(master=right_panel, text=invalid_text,anchor="w", justify="left", text_color="#601E88",font=("Arial Bold", 15,))
    if invalid_var.get() :
        label.pack(anchor="w",pady=(10,0),padx=(75, 0))
    else :
        label.pack_forget()

# Left Panel 
left_panel = CTkFrame(master=app, width=300, height=480, fg_color="black")
left_panel.pack_propagate(0)
left_panel.pack(expand=True, side="left")
CTkLabel(master=left_panel, text="", image=side_img).pack(expand=True, fill="both")

# Right Panel (Login Form)
right_panel = CTkFrame(master=app, width=300, height=480, fg_color="#ffffff")
right_panel.pack_propagate(0)
right_panel.pack(expand=True, side="right")

# Display Login Form Initially
display_login_form()

# Run the Application
app.mainloop()