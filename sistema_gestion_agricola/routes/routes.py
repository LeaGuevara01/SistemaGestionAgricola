from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Cambiar de 'react_app.html' a 'index.html'
    return render_template('index.html')

@main.route('/vite')
def vite_app():
    return render_template('vite.html')