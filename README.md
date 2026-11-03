# Monthly Top Tracks Backup

A GitHub Actions workflow that runs on the 1st of each month and saves the previous month's top songs to private Spotify playlists.

## Monthly behavior

The month below is the month being backed up.

- Regular months: creates a short-term (last ~4 weeks) playlist.
- June: creates short-term and medium-term (last ~6 months) playlists.
- December: creates short-term, medium-term, and long-term (last ~1 year) playlists.

Every run creates new playlists, so triggering the workflow manually twice in a month duplicates them.

## Setup

Requires Spotify Premium (for Development Mode apps).

1. Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) with redirect URI `http://127.0.0.1:8888/callback`.
2. Set `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` and `SPOTIPY_REDIRECT_URI` in `.env`, then:

   ```sh
   pip install -r requirements.txt
   python get_refresh_token.py  # prints the refresh token
   gh secret set -f .env
   gh secret set SPOTIPY_REFRESH_TOKEN
   ```

3. On a fork, enable workflows in the Actions tab.

If the refresh token expires, re-run `get_refresh_token.py` and `gh secret set SPOTIPY_REFRESH_TOKEN`.

To change the timezone (default `Asia/Tokyo`), edit both `timezone` and `env.TZ` in `.github/workflows/main.yml`.

## Disclaimer

- "Spotify" is a trademark or registered trademark of Spotify AB. This project is not affiliated with Spotify AB in any way.
- This tool is intended for each user to run on their own Spotify account.
- Compliance with Spotify's terms and policies is the user's responsibility.

## License

This software is licensed under the [MIT License](LICENSE).
