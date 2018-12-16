import os

import click
from app import create_app
from app.models import User
from dotenv import load_dotenv
from itsdangerous import JSONWebSignatureSerializer
from mongoengine.errors import NotUniqueError, ValidationError
from werkzeug.security import generate_password_hash

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


app = create_app(os.getenv('FLASK_ENV'))


def generate_auth_token(email):
    s = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
    return s.dumps({'email': email})


@app.cli.command()
@click.argument('email')
@click.argument('password')
def create_user(email, password):
    try:
        # Create new user in MongoDB
        new_user = User()
        new_user.email = email
        new_user.password = generate_password_hash(password)
        new_user.token = generate_auth_token(email).decode('utf-8')
        new_user.save()
        click.echo(f'New User "{email}" created in Database')
    except NotUniqueError:
        click.echo(f'User "{email}" already exists!')
    except ValidationError as ve:
        click.echo(ve)
