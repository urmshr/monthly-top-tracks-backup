import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

JST = ZoneInfo("Asia/Tokyo")


def get_target_month():
    """Return a date in the previous month (JST), which is the month to back up."""
    first_of_this_month = datetime.now(JST).replace(day=1)
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
        scope="user-top-read playlist-modify-private",
        open_browser=False,
    )

    # Refresh the access token and use it for this run.
    token_info = auth_manager.refresh_access_token(refresh_token)
    access_token = token_info.get("access_token")
    if not access_token:
        print("Error: Failed to refresh access token.")
        sys.exit(1)

    return spotipy.Spotify(auth=access_token)


def main():
    # 1. Back up the previous month (the workflow runs on the 1st, JST)
    target = get_target_month()
    print(f"Starting Monthly Top Tracks Backup for {target:%Y-%m}...")
    sp = get_spotify_client()
    user_id = sp.me()["id"]

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
    for time_range in time_ranges:
        top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
        track_uris = [track["uri"] for track in top_tracks["items"]]

        if not track_uris:
            print(f"No tracks found for {time_range}. Skipping...")
            continue

        term_label = term_labels[time_range]
        if time_range == "short_term":
            date_str = date_str_short
        elif time_range == "medium_term":
            date_str = date_str_medium
        else:
            date_str = date_str_long
        playlist_name = f"Top Tracks ({date_str})"

        new_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Automated backup of my top tracks from the {term_label} for {date_str}",
        )

        # 3. Add tracks to playlist
        sp.playlist_add_items(new_playlist["id"], track_uris)

        print(f"Successfully created playlist: {playlist_name}")


if __name__ == "__main__":
    main()
