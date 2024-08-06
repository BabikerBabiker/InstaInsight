import instaloader
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import threading

def login_instagram(username, password):
    L = instaloader.Instaloader()
    try:
        L.login(username, password)
        profile = instaloader.Profile.from_username(L.context, username)
        followers = set(profile.get_followers())
        following = set(profile.get_followees())
        not_following_back = list(following - followers)
        return True, [user.username for user in not_following_back]
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        code = simpledialog.askstring("2FA Required", "Enter the 2FA code:")
        L.two_factor_login(code)
        return login_instagram(username, password)
    except instaloader.exceptions.BadCredentialsException:
        return False, ["Invalid credentials."]
    except instaloader.exceptions.ConnectionException:
        return False, ["Connection error."]
    except instaloader.exceptions.ProfileNotExistsException:
        return False, ["Profile does not exist."]
    except Exception as e:
        return False, [f"An error occurred: {e}"]

def update_result_text(message):
    result_text.configure(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, message)
    result_text.configure(state=tk.DISABLED)

def show_logging_in():
    global dot_count, logging_in_id, current_message
    dot_count = (dot_count + 1) % 4
    dots = "." * dot_count
    update_result_text(f"{current_message}{dots}")
    logging_in_id = root.after(500, show_logging_in)

def hide_logging_in():
    if logging_in_id is not None:
        root.after_cancel(logging_in_id)
    result_text.configure(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.configure(state=tk.DISABLED)

def on_login():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Error", "Username and password cannot be empty.")
        return

    def run_login():
        global current_message
        current_message = "Logging you in"
        show_logging_in()
        try:
            success, result = login_instagram(username, password)
            hide_logging_in()
            if success:
                current_message = "Login Successful"
                update_result_text(current_message)
                root.after(2000, lambda: analyze_instagram(username, password))
            else:
                messagebox.showerror("Error", "\n".join(result))
        except Exception as e:
            hide_logging_in()
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run_login, daemon=True).start()

def analyze_instagram(username, password):
    global current_message
    current_message = "Analyzing your Instagram"
    show_logging_in()
    
    def run_analysis():
        success, result = login_instagram(username, password)
        hide_logging_in()
        if success:
            sorted_result = sorted(result)
            update_result_text("\n".join(sorted_result))
        else:
            messagebox.showerror("Error", "\n".join(result))
    
    threading.Thread(target=run_analysis, daemon=True).start()

def show_results():
    login_frame.pack_forget()  # Hide the login form
    result_frame.pack(fill=tk.BOTH, expand=True)  # Show the result output

root = tk.Tk()
root.title("InstaInsight")
root.geometry("500x600")
root.configure(bg="#c0d4e4")  # Blue background

# Set up styles directly for tk widgets
label_font = ("Helvetica", 12)
entry_font = ("Helvetica", 12)

# Create a frame for centering the login area with a white background
center_frame = tk.Frame(root, bg="white", padx=20, pady=20)
center_frame.place(relx=0.5, rely=0.5, anchor="center")

# Create login frame inside the center_frame
login_frame = tk.Frame(center_frame, padx=20, pady=20)
login_frame.pack(fill=tk.BOTH, expand=True)
tk.Label(login_frame, text="InstaInsight", font=("Helvetica", 18, "bold")).pack(pady=(20, 10))
tk.Label(login_frame, text="Find the users who don't follow you back.", font=label_font).pack(pady=5)

tk.Label(login_frame, text="Username:", font=label_font).pack(anchor='w', padx=5, pady=5)
username_entry = tk.Entry(login_frame, width=30, font=entry_font, fg="#000000", bg="#ffffff")  # Use tk.Entry to avoid blue highlighting
username_entry.pack(padx=5, pady=5)
tk.Label(login_frame, text="Password:", font=label_font).pack(anchor='w', padx=5, pady=5)
password_entry = tk.Entry(login_frame, show="*", width=30, font=entry_font, fg="#000000", bg="#ffffff")  # Use tk.Entry to avoid blue highlighting
password_entry.pack(padx=5, pady=5)
login_button = tk.Button(login_frame, text="Login", command=lambda: [on_login(), show_results()])
login_button.pack(pady=10)

# Create results frame
result_frame = tk.Frame(root, bg="#c0d4e4")  # Blue background for the result frame
result_frame.pack_forget()  # Hide initially

# Add header to result_frame
header_label = tk.Label(result_frame, text="Users Not Following Back", font=("Helvetica", 16, "bold"), bg="#c0d4e4")
header_label.pack(pady=10)

# Add ScrolledText widget with updated styling
result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=60, height=15, font=("Helvetica", 12), state=tk.DISABLED, bg="#ffffff", borderwidth=2, relief="sunken")
result_text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

dot_count = 0
logging_in_id = None
current_message = ""

root.mainloop()