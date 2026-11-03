import os
import sys
from datetime import datetime, timedelta

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Also used by get_refresh_token.py, so the issued token has these permissions.
# playlist-read-private is needed to see the (private) backup playlists when skipping existing ones.
SCOPE = "user-top-read playlist-modify-private playlist-read-private"


def get_target_month():
    """Return a date in the previous month, which is the month to back up.

    Uses local time, so the timezone comes from the TZ environment variable
    (set in the workflow) or the machine's timezone when run locally.
    """
    first_of_this_month = datetime.now().replace(day=1)
    return first_of_this_month - timedelta(days=1)


def get_spotify_client():
    """Authenticate using the refresh token from environment variables."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    refresh_token = os.getenv("SPOTIPY_REFRESH_TOKEN")

    if not all([client_id, client_secret, redirect_uri, refresh_token]):
        print("Error: Missing environment variables.")
        sys.exit(1)

    # Configure automatic access token refresh using the refresh token
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        open_browser=False,
    )

    # Refresh the access token and use it for this run.
    token_info = auth_manager.refresh_access_token(refresh_token)
    access_token = token_info.get("access_token")
    if not access_token:
        print("Error: Failed to refresh access token.")
        sys.exit(1)

    return spotipy.Spotify(auth=access_token)


def get_existing_playlist_names(sp):
    """Return the names of all playlists in the current user's library."""
    names = set()
    page = sp.current_user_playlists(limit=50)
    while page:
        names.update(p["name"] for p in page["items"] if p)
        page = sp.next(page) if page["next"] else None
    return names


def main():
    # 1. Back up the previous month (the workflow runs on the 1st)
    target = get_target_month()
    print(f"Starting Monthly Top Tracks Backup for {target:%Y-%m}...")
    sp = get_spotify_client()

    if target.month == 12:
        time_ranges = ["short_term", "medium_term", "long_term"]
    elif target.month == 6:
        time_ranges = ["short_term", "medium_term"]
    else:
        time_ranges = ["short_term"]

    term_labels = {
        "short_term": "last ~4 weeks",
        "medium_term": "last ~6 months",
        "long_term": "last ~1 year",
    }

    # 2. Fetch top 50 tracks and create playlists per time range
    date_str_short = target.strftime("%Y%m")
    date_str_long = target.strftime("%Y")
    if target.month == 6:
        date_str_medium = f"{target.year}01-{target.year}06"
    elif target.month == 12:
        date_str_medium = f"{target.year}07-{target.year}12"
    # Skip playlists that already exist, so retries and manual re-runs don't duplicate them.
    existing_names = get_existing_playlist_names(sp)

    for time_range in time_ranges:
        term_label = term_labels[time_range]
        if time_range == "short_term":
            date_str = date_str_short
        elif time_range == "medium_term":
            date_str = date_str_medium
        else:
            date_str = date_str_long
        playlist_name = f"Top Tracks ({date_str})"

        if playlist_name in existing_names:
            print(f"Playlist already exists: {playlist_name}. Skipping...")
            continue

        top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
        track_uris = [track["uri"] for track in top_tracks["items"]]

        if not track_uris:
            print(f"No tracks found for {time_range}. Skipping...")
            continue

        # POST /me/playlists: POST /users/{id}/playlists is unavailable to
        # Development Mode apps created after Spotify's February 2026 changes.
        new_playlist = sp.current_user_playlist_create(
            name=playlist_name,
            public=False,
            description=f"Automated backup of my top tracks from the {term_label} for {date_str}",
        )

        # 3. Add tracks to playlist
        sp.playlist_add_items(new_playlist["id"], track_uris)

        print(f"Successfully created playlist: {playlist_name}")


if __name__ == "__main__":
    main()
