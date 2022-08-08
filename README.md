# Honey Consumer

Grab Honey tasks off the pub sub queue, digest them, and load them into a MySQL database.

## Getting Started

1. Make a copy of `start.sh.sample` and change it's name to `start.sh`
2. Edit `start.sh` and fill in your database creds
3. Create a service account in GCP with PubSub Read permissions.
4. Create a json key and place it in the root of this repo
5. Ensure that `GOOGLE_SERVICE_JSON` actually cats out the json key.

Then just `docker build` & `docker run`
