import argparse
from azure.identity import AzureDeveloperCliCredential
import httpx
from fastapi import FastAPI, Request

app = FastAPI()

# Function to update redirect URIs in Azure AD B2C using Microsoft Graph API
def update_redirect_uris(credential, app_id, uri):
    access_token = credential.get_token("https://graph.microsoft.com/.default").token
    response = httpx.patch(
        f"https://graph.microsoft.com/v1.0/applications/{app_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "web": {
                "redirectUris": [
                    "http://localhost:5000/oauth2/authresp",
                    f"{uri}/oauth2/authresp",
                ]
            }
        },
    )
    if response.status_code == 204:
        print(f"Successfully updated redirect URIs for application {app_id}")
    else:
        print(f"Failed to update redirect URIs: {response.status_code} - {response.text}")

# Define the callback route in FastAPI for handling OAuth response
@app.get("/oauth2/authresp")
async def auth_callback(request: Request):
    # Extract the 'code' from the query parameters
    code = request.query_params.get("code")
    if not code:
        return {"error": "Authorization code not found in request"}

    # Exchange the authorization code for tokens
    async with httpx.AsyncClient() as client:
        token_url = "https://wjpllc.b2clogin.com/wjpllc.onmicrosoft.com/oauth2/v2.0/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": "<your-client-id>",  # Replace with your client ID
            "client_secret": "<your-client-secret>",  # Replace with your client secret
            "redirect_uri": "https://wjpllc.b2clogin.com/wjpllc.onmicrosoft.com/oauth2/authresp",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await client.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            tokens = response.json()
            return {"message": "Authentication successful", "tokens": tokens}
        else:
            return {"error": f"Failed to exchange authorization code: {response.text}"}

if __name__ == "__main__":
    # Argument parser for updating redirect URIs
    parser = argparse.ArgumentParser(
        description="Add a redirect URI to a registered application and run FastAPI server",
        epilog="Example: auth_update.py --appid 123 --uri https://abc.azureservices.net",
    )
    parser.add_argument(
        "--appid",
        required=True,
        help="Required. ID of the application to update.",
    )
    parser.add_argument(
        "--uri",
        required=True,
        help="Required. URI of the deployed application.",
    )
    args = parser.parse_args()

    # Update redirect URIs before running the FastAPI app
    credential = AzureDeveloperCliCredential()

    print(
        f"Updating application registration {args.appid} with redirect URI for {args.uri}"
    )
    update_redirect_uris(credential, args.appid, args.uri)

    # Start the FastAPI application after updating redirect URIs
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
