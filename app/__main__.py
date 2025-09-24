from app import create_app

app = create_app()

if __name__ == "__main__":
    # WICHTIG: Host 0.0.0.0, sonst ist er nur intern erreichbar
    app.run(host="0.0.0.0", port=5000)
