# Monthly Top Tracks Backup

A script that runs on the 1st of each month (JST) and saves the previous month's top songs to a Spotify playlist.

## Monthly behavior

The month below is the month being backed up.

- Regular months: creates a short-term (last ~4 weeks) playlist.
- June: creates short-term and medium-term (last ~6 months) playlists.
- December: creates short-term, medium-term, and long-term (last ~1 year) playlists.

Every run creates new playlists, so triggering the workflow manually twice in a month duplicates them.

## Environment variables

- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI`
- `SPOTIPY_REFRESH_TOKEN`

## Refresh token

Generate it locally (and regenerate it when it expires) with the other three variables set in `.env`:

```sh
python get_refresh_token.py
gh secret set SPOTIPY_REFRESH_TOKEN  # paste the printed token
```

## Disclaimer

- "Spotify" is a trademark or registered trademark of Spotify AB. This project is not affiliated with Spotify AB in any way.
- This tool is intended for each user to run on their own Spotify account.
- Compliance with Spotify's terms and policies is the user's responsibility.

## License

This software is licensed under the [MIT License](LICENSE).
