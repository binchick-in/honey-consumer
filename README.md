# Honey Consumer

Grab Honey tasks off the pub sub queue, digest them, and load them into a MySQL database.

## Getting Started


1. Copy `.env.example` to `.env` and populate it
2. Create a service account in GCP with PubSub Read permissions.
3. Create a json key and populate `GOOGLE_SERVICE_JSON` with it in `.env`
4. `make run`
