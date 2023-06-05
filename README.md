# removebang
Scalable Microservices Web to Remove Background 

## Setting up a cool development env

### Python services

Python services including `bg-remover` and `web` use `pip-tools` to manage dependencies. If you will not modify dependencies, you can only use `pip`.

- Using `pip` only,
  
  ```
  python -m venv .venv
  . .venv/bin/activate  # adjust this according to your shell
  pip install -r requirements.txt
  ```

- Using `pip-tools`

  Run the same command as the above,

  ```
  pip install pip-tools
  ```

  When you want to add/remove/update dependencies, you do so by modifying requirements.in. After modifying it, compile by running `pip-compile requirements.in`, then sync with your current environment using `pip-sync requirements.txt`. When needed, you can also run the same command but using `dev-requirements.{in,txt}` (for requirements like linters, convenient CLIs, etc.).

# Run using docker-compose

First, make sure you have `key.json` file at the root of the repository (adjacent to the `docker-compose.yaml` file). If you don't have it already, you can generate one by setting up `gcloud` CLI and create a service account (see it [here](https://support.google.com/a/answer/7378726?hl=en)).

    docker compose build
    docker compose up

# Access the Website

You can access the website in your `localhost:7000`
