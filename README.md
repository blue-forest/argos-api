
# Simple Argos HTTP API
Expose a translation service over HTTP using the (Argos Python library)[https://github.com/argosopentech/argos-translate]

Environment variables:
- `ARGOS_LANGUAGES`: Comma-separated list of languages to expose (required)
- `ARGOS_TOKEN`: Token to use for authentication (none if not set)
- `ARGOS_PORT`: Port to run the API on (default is 8080)

Volume for persistance: `/root/.local/cache/argos-translate/`
