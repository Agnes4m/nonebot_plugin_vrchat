# Step 1. We begin with creating a Configuration, which contains the username and password for authentication.
import vrchatapi
from vrchatapi.api import authentication_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from jsonify import convert

from http.cookiejar import LWPCookieJar

def save_cookies(client: vrchatapi.ApiClient, filename: str)
    # Create a new cookie jar to current load session cookies into
    cookie_jar = LWPCookieJar(filename=filename)

    # Load cookies from ApiClient cookie jar into our new one
    for cookie in client.rest_client.cookie_jar:
      cookie_jar.set_cookie(cookie)

    # Then we save to the file given as a param
    cookie_jar.save()

def load_cookies(client: vrchatapi.ApiClient, filename: str)
    # Create a new cookie jar to load cookies from file
    cookie_jar = LWPCookieJar(filename=filename)
    
    # Load cookies if they exist, otherwise make a new cookie_jar file
    try:
        cookie_jar.load()
    except FileNotFoundError:
        cookie_jar.save()
        return

    # Transfer cookies we loaded to our session cookie jar
    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)

configuration = vrchatapi.Configuration(
    username = "username",
    password = "password",
)

# Step 2. VRChat consists of several API's (WorldsApi, UsersApi, FilesApi, NotificationsApi, FriendsApi, etc...)
# Here we enter a context of the API Client and instantiate the Authentication API which is required for logging in.

# Enter a context with an instance of the API client
with vrchatapi.ApiClient(configuration) as api_client:
    # We should try log in first :)
    load_cookies(api_client, "./cookies.txt")

    # Instantiate instances of API classes
    auth_api = authentication_api.AuthenticationApi(api_client)

    try:
        # Step 3. Calling getCurrentUser on Authentication API logs you in if the user isn't already logged in.
        current_user = auth_api.get_current_user()

    except ValueError:
        # Step 3.5. Calling email verify2fa if the account has 2FA disabled
        auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
        current_user = auth_api.get_current_user()
        
        save_cookies(api_client, "./cookies.txt")
    except UnauthorizedException as e:
        print(e)
        if e.status == 200:
            if "Email 2 Factor Authentication" in e.reason:
                # Step 3.5. Calling email verify2fa if the account has 2FA disabled
                auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
            elif "2 Factor Authentication" in e.reason:
                # Step 3.5. Calling verify2fa if the account has 2FA enabled
                auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
            current_user = auth_api.get_current_user()
            save_cookies(api_client, "./cookies.txt")
        else:
            print("Exception when calling API: %s\n", e)
    except vrchatapi.ApiException as e:
        print("Exception when calling API: %s\n", e)

    print("Logged in as:", current_user.display_name)