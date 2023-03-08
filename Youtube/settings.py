INSTALLED_APPS = [
    # ...
    'youtube_auth',
]

# Ajoutez ces variables d'environnement avec vos propres informations d'identification Google
GOOGLE_CLIENT_ID = '925779292051-dlogeud1h4ks9u5t7p0go9qi5i79cefr.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_AUTH_REDIRECT_URI = 'https://localhost:8000/youtube_/callback/'
GOOGLE_AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_SCOPE = ['https://www.googleapis.com/auth/youtube.force-ssl']