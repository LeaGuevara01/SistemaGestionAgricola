# sistema_gestion_agricola/routes/routes.py
from flask import Blueprint, render_template, request, current_app

main = Blueprint('main', __name__)

@main.route('/')
def index():
    use_react = current_app.config.get('USE_REACT', False)
    frontend_mode = request.args.get('mode', current_app.config.get('FRONTEND_MODE', 'html'))
    if use_react or frontend_mode == 'react':
        return render_template('react_app.html')
    else:
        return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    use_react = current_app.config.get('USE_REACT', False)
    frontend_mode = request.args.get('mode', current_app.config.get('FRONTEND_MODE', 'html'))
    if use_react or frontend_mode == 'react':
        return render_template('react_app.html')
    else:
        return render_template('dashboard.html')

@main.route('/react')
@main.route('/react/<path:path>')
def react_app(path=''):
    return render_template('react_app.html')

@main.route('/html')
@main.route('/html/<path:path>')
def html_app(path=''):
    return render_template('index.html')
