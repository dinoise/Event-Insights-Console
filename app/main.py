from os import environ, getenv

from __init__ import create_app

config_name = getenv("FLASK_ENV", "dev")
print(f"ENV {config_name}")

app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 8080)))
