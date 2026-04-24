from app import create_app

# instantiate the flask application to initialize all extensions
app = create_app()

# push the application context globally for the worker
app.app_context().push()
