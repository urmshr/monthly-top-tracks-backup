import os
import sys
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def is_last_day_of_month():
    """Return True if today is the last day of the month."""
    today = datetime.now()
    # Get tomorrow's date
    next_day = today + timedelta(days=1)
    # If tomorrow is the first day of next month, today is the last day
    return next_day.day == 1


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
    # 1. Check if today is the last day of the month
    if not is_last_day_of_month():
        print("Today is not the last day of the month. Skipping...")
        return

    print("Starting Monthly Top Tracks Backup...")
    today = datetime.now()
    sp = get_spotify_client()
    user_id = sp.me()["id"]

    if today.month == 12:
        time_ranges = ["short_term", "medium_term", "long_term"]
    elif today.month == 6:
        time_ranges = ["short_term", "medium_term"]
    else:
        time_ranges = ["short_term"]

    term_labels = {
        "short_term": "last ~4 weeks",
        "medium_term": "last ~6 months",
        "long_term": "last ~1 year",
    }


    # 2. Fetch top 50 tracks and create playlists per time range
    date_str_short = today.strftime("%Y%m")
    date_str_long = today.strftime("%Y")
    if today.month == 6:
        date_str_medium = f"{today.year}01-{today.year}06"
    elif today.month == 12:
        date_str_medium = f"{today.year}07-{today.year}12"
    else:
        date_str_medium = f"Mid {today.strftime('%Y')}"
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
