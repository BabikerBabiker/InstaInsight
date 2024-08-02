import os
import instaloader
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import threading

def read_credentials(file_path):
    credentials = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                credentials[key] = value
    except FileNotFoundError:
        raise FileNotFoundError("Credentials file not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the credentials: {e}")
    return credentials

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

def show_logging_in():
    global dot_count, logging_in_id
    dot_count = (dot_count + 1) % 4
    dots = "." * dot_count
    result_text.configure(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Logging you in{dots}")
    result_text.configure(state=tk.DISABLED)
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
        show_logging_in()
        try:
            credentials = read_credentials("credentials.txt")
            username = credentials.get("username")
            password = credentials.get("password")
            if not username or not password:
                messagebox.showerror("Error", "Username or password not found in the credentials file.")
                hide_logging_in()
                return
            success, result = login_instagram(username, password)
            hide_logging_in()
            if success:
                result_text.configure(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "\n".join(result))
                result_text.configure(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "\n".join(result))
        except Exception as e:
            hide_logging_in()
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run_login, daemon=True).start()

root = tk.Tk()
root.title("InstaInsight")
root.geometry("500x500")
root.configure(bg="#e5e5e5")
header_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=10)
header_frame.pack(fill=tk.X)
header_label = tk.Label(header_frame, text="InstaInsight", font=("Helvetica", 16, "bold"), bg="#ffffff")
header_label.pack()
description_label = tk.Label(header_frame, text="Find the users who dont follow you back.", font=("Helvetica", 12), bg="#ffffff")
description_label.pack(pady=5)
form_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=10)
form_frame.pack(pady=10)
tk.Label(form_frame, text="Username:", bg="#ffffff", font=("Helvetica", 12)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
username_entry = tk.Entry(form_frame, width=40, font=("Helvetica", 12))
username_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Label(form_frame, text="Password:", bg="#ffffff", font=("Helvetica", 12)).grid(row=1, column=0, sticky='e', padx=5, pady=5)
password_entry = tk.Entry(form_frame, show="*", width=40, font=("Helvetica", 12))
password_entry.grid(row=1, column=1, padx=5, pady=5)
login_button = tk.Button(form_frame, text="Login", command=on_login, font=("Helvetica", 12), bg="#007ACC", fg="#ffffff", relief=tk.RAISED, bd=2)
login_button.grid(row=2, columnspan=2, pady=10)
results_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=10)
results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
result_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=60, height=15, font=("Helvetica", 12), state=tk.DISABLED, bg="#f0f0f0", borderwidth=2, relief="sunken")
result_text.pack(fill=tk.BOTH, expand=True)
dot_count = 0
logging_in_id = None
root.mainloop()