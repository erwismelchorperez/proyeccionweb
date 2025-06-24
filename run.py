from app import create_app

app = create_app()

if __name__ == "__main__":
    print(app.url_map)
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True)
