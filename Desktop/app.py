from customtkinter import *
from PIL import Image

# Initialize Application
app = CTk()
app.geometry("600x480")
app.iconbitmap("./attendance.ico")
app.title("SmartLab")

# Load Images
side_img_data = Image.open("side-img.png")
email_icon_data = Image.open("email-icon.png")
password_icon_data = Image.open("password-icon.png")
session_icon_data = Image.open("session.png")

side_img = CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))
email_icon = CTkImage(dark_image=email_icon_data, light_image=email_icon_data, size=(20, 20))
password_icon = CTkImage(dark_image=password_icon_data, light_image=password_icon_data, size=(17, 17))
session_icon = CTkImage(dark_image=session_icon_data, light_image=session_icon_data, size=(17, 17))

# Function to Replace the Right Frame
def on_login_click():
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
        text="Welcome to the Dashboard!",
        font=("Arial", 16),
        text_color="#601E88"
    ).pack(pady=10)

    CTkButton(
        master=right_panel,
        text="Logout",
        fg_color="#E44982",
        hover_color="#601E88",
        text_color="white",
        command=logout
    ).pack(pady=20)


def logout():
    for widget in right_panel.winfo_children():
        widget.destroy()
    display_login_form()

def display_login_form():
    CTkLabel(master=right_panel, text="Welcome Back!", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))

    CTkLabel(master=right_panel, text="  Email", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=email_icon, compound="left").pack(anchor="w", pady=(38, 0), padx=(25, 0))
    CTkEntry(master=right_panel, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000").pack(anchor="w", padx=(25, 0))

    CTkLabel(master=right_panel, text="  Password", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=password_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
    CTkEntry(master=right_panel, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000", show="*").pack(anchor="w", padx=(25, 0))

    CTkLabel(master=right_panel, text="  Session", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=session_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
    CTkEntry(master=right_panel, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000").pack(anchor="w", padx=(25, 0))

    CTkButton(
        master=right_panel,
        text="Login",
        fg_color="#601E88",
        hover_color="#E44982",
        font=("Arial Bold", 12),
        text_color="#ffffff",
        width=225,
        command=on_login_click  # Attach the login function here
    ).pack(anchor="w", pady=(40, 0), padx=(25, 0))

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
