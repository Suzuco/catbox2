# Catbox 2

A minimalistic HTTP file server with Flask.

## Configuration

Change in source

    app.config["storage"] = "box/"

## Deployment

Running the server with `nginx` and `gunicorn` are generally recommended instead of running the script directly, despite being also viable.

    $ gunicorn -b 0.0.0.0:25252 app:app

With `nginx`, you will need to create a port map for the web application, a static content `location` for the storage configured as in the script, and (preferably) allow larger `client_max_body_size`.
