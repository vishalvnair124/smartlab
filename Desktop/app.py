from customtkinter import *
from PIL import Image
import uuid



# Initialize Application
app = CTk()
app.geometry("600x480")
app.iconbitmap("./attendance.ico")
app.title("SmartLab")

invalid_var = BooleanVar(value=False) 

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

def send_login(email, password, session):
    # Get Email and Password from Entry Fields
    mac_add = get_mac_address()
    
    respons = {
               "response":200,
               "session_end":"12-12-12",
               "name" : "John",
               "email" : "vishalvnair124@gmail.com"
              }
    return respons

def send_logout(response_from):
    print("Logout Request Send",response_from)
    respons = {
               "response":200
              }
    return respons

def device_registration(email,password):
    mac_add = get_mac_address()
    print(email,password,mac_add)
    response = {
               "response":200
              }
    return response

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
        response = send_login(email, password, session)
        if response["response"] == 200:
            display_logedin(response)
        else:
            invalid_var.set(True)
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

    label = CTkLabel(master=right_panel, text="Invalid credintial",anchor="w", justify="left", text_color="#601E88",font=("Arial Bold", 15,))
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