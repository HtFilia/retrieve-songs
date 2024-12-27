# Stream-Redirect

The project is separated in 3 folders:

- ==download==: the firefox extension requesting the backend server through HTTP requests.
- ==server==: the backend server deciphering the youtube streams (be it audio or video) into chunks and then concatening them into a single .m4a (audio) or .mp4 (video) file.
- ==web==: the client webapp connecting to a server handling the download (local or distant) for organizing our downloads through a graphical interface.

## Firefox extension usage

Get your API_KEY and API_SECRET through [https://addons.mozilla.org/](https://addons.mozilla.org/) and replace them in the following commands

> cd download
> web-ext sign --channel=unlisted --api-key=\$API_KEY --api-secret=\$API_SECRET

## Server usage

> cd server
> python3 app.py
