import os
import instaloader


def read_credentials(file_path):
    """Read Instagram credentials from a file."""
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

CREDENTIALS_FILE = "credentials.txt"

try:
    credentials = read_credentials(CREDENTIALS_FILE)
    username = credentials.get("username")
    password = credentials.get("password")

    if not username or not password:
        raise ValueError("Username or password not found in the credentials file.")
except Exception as e:
    print(e)
    exit(1)

L = instaloader.Instaloader()

try:
    print("Attempting to log in...")
    L.login(username, password)
    print("Login successful.")
    print("--------------------------------")

    profile = instaloader.Profile.from_username(L.context, username)

    followers = set(profile.get_followers())
    following = set(profile.get_followees())

    not_following_back = list(following - followers)

    print("Users you follow who don't follow you back:")
    for user in not_following_back:
        print(user.username)

except instaloader.exceptions.TwoFactorAuthRequiredException:
    print(
        "Two-factor authentication is required. Please enter the verification code sent to your device."
    )
    code = input("Enter the 2FA code: ")
    L.two_factor_login(code)

except instaloader.exceptions.BadCredentialsException:
    print("Invalid credentials. Please check your username and password.")
except instaloader.exceptions.ConnectionException:
    print("Connection error. Please check your internet connection.")
except instaloader.exceptions.ProfileNotExistsException:
    print("Profile does not exist. Please check your username.")
except Exception as e:
    print(f"An error occurred: {e}")