"""
Access tokens will expire after a while. The Auth API may give you a refresh token
that you can use to obtain a "fresh" access token.

A non-confidential app cannot refresh its token, you'll need to re-authenticate.
"""

from mondo.authorization import (generate_mondo_auth_url,
                                 exchange_authorization_code_for_access_token)

if __name__ == '__main__':
    print("Utility to fetch the access token for testing purposes")

    client_id = input("Insert your client_id: ")
    client_secret = input("Insert your client_secret: ")
    redirect_uri = input("Insert your redirect_uri: ")

    auth_url = generate_mondo_auth_url(
        client_id=client_id,
        redirect_uri=redirect_uri
    )

    print("Open your browser here: %s" % auth_url)
    print("And follow the login.")
    print("\n")
    auth_code = input("Then paste the resulting auth code here: ")

    access_token, refresh_token = exchange_authorization_code_for_access_token(
        client_id=client_id,
        client_secret=client_secret,
        authorization_code=auth_code,
        redirect_uri=redirect_uri
    )

    print("\n")
    print("SUCCESS!")
    print("\n")
    print("Your access token is: %s" % access_token)
    print("\n")
    print("Your refresh token is: %s" % refresh_token)
