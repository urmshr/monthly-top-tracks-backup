import os
import sys
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Must match the scope used in main.py so the issued token has the same permissions.
SCOPE = "user-top-read playlist-modify-private"


def main():
    """Run the OAuth flow locally and print a fresh refresh token."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        print("Error: Missing environment variables.")
        print("Set SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET and SPOTIPY_REDIRECT_URI")
        print("(in .env or your shell) before running this script.")
        sys.exit(1)

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        # Don't reuse a stale .cache so we always mint a brand-new token.
        cache_path=".cache-refresh",
        open_browser=True,
    )

    # Opens the browser, waits for the redirect, then exchanges the code.
    token_info = auth_manager.get_access_token(as_dict=True, check_cache=False)
    refresh_token = token_info.get("refresh_token")

    if not refresh_token:
        print("Error: No refresh token returned. Authorization may have failed.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("New refresh token (set this as the GitHub secret):")
    print("\n  SPOTIPY_REFRESH_TOKEN=" + refresh_token + "\n")
    print("Update it with:")
    print("  gh secret set SPOTIPY_REFRESH_TOKEN")
    print("(then paste the token value when prompted)")
    print("=" * 60)


if __name__ == "__main__":
    main()
