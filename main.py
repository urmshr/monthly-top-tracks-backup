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

    # Set the refresh token
    auth_manager.refresh_access_token(refresh_token)

    return spotipy.Spotify(auth_manager=auth_manager)


def main():
    # 1. Check if today is the last day of the month
    if not is_last_day_of_month():
        print("Today is not the last day of the month. Skipping...")
        return

    print("Starting Monthly Top Tracks Backup...")
    sp = get_spotify_client()
    user_id = sp.me()["id"]

    # 2. Fetch recent (approximately last 4 weeks) top 50 tracks
    top_tracks = sp.current_user_top_tracks(limit=50, time_range="short_term")

    track_uris = [track["uri"] for track in top_tracks["items"]]

    if not track_uris:
        print("No tracks found. Exiting.")
        return

    # 3. Create playlist
    date_str = datetime.now().strftime("%Y-%m")
    playlist_name = f"Top Tracks ({date_str})"

    new_playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description=f"Automated backup of my short term (approximately last 4 weeks) top tracks for {date_str}",
    )

    # 4. Add tracks to playlist
    sp.playlist_add_items(new_playlist["id"], track_uris)

    print(f"Successfully created playlist: {playlist_name}")


if __name__ == "__main__":
    main()
