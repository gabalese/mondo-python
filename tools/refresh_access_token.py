"""
Quick and dirty script to re-create a workable OAuth 2 flow and get
the access token we need to use the Mondo API
"""

from mondo.authorization import refresh_access_token

if __name__ == '__main__':
    client_id = input("Insert your client_id: ")
    client_secret = input("Insert your client_secret: ")
    refresh_token = input("Insert your refresh token here: ")

    access_token, refresh_token = refresh_access_token(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token
    )

    print("SUCCESS!")
    print("\n")
    print("Your new access token is: ")
    print(access_token)
    print("\n")
    print("Your new refresh token is: ")
    print(refresh_token)

