from Farmica_app import app
app.secret_key = 'thisissecretkey'

if __name__ == "__main__":
    app.run(debug=True)

# port=80000