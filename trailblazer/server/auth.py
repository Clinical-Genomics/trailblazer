# -*- coding: utf-8 -*-
from flask import current_app
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized
from flask import flash, redirect, request, session, url_for
from flask_login import (LoginManager, login_user, login_required, logout_user,
                         AnonymousUserMixin)


class AnonymousUser(AnonymousUserMixin):

    def __init__(self):
        self.name = 'Paul T. Anderson'
        self.email = 'pt@anderson.com'

    @property
    def is_authenticated(self):
        if current_app.config.get('LOGIN_DISABLED'):
            return True
        else:
            return False


class AuthManager(object):

    """Provide usermanagement for a Flask app.

    Args:
        manager (alchy.Manager): database connection object

    ENV variables:
      - GOOGLE_OAUTH_CLIENT_ID
      - GOOGLE_OAUTH_CLIENT_SECRET
    """

    def __init__(self, manager):
        super(AuthManager, self).__init__()
        self.db = manager
        self.login_manager = None
        self.blueprint = None
        self.setup()

    def init_app(self, app):
        app.register_blueprint(self.blueprint, url_prefix='/login')

        @app.route('/api/v1/login')
        def login():
            """Redirect to the Google login page."""
            # store potential next param URL in the session
            if 'next' in request.args:
                session['next_url'] = request.args['next']
            return redirect(url_for('google.login'))

        @app.route('/api/v1/logout')
        @login_required
        def logout():
            logout_user()
            flash('You have logged out', 'info')
            return redirect(request.args.get('next') or url_for('index'))

        self.login_manager.init_app(app)

    def setup(self):
        self.blueprint = make_google_blueprint(scope=['profile', 'email'])

        # setup login manager
        self.login_manager = LoginManager()
        self.login_manager.login_view = 'login'
        self.login_manager.anonymous_user = AnonymousUser

        @self.login_manager.user_loader
        def load_user(user_id):
            return self.db.User.get(int(user_id))

        @oauth_authorized.connect_via(self.blueprint)
        def google_loggedin(blueprint, token, this=self):
            """Create/login local user on successful OAuth login."""
            if not token:
                flash(f"Failed to log in with {blueprint.name}", 'danger')
                return redirect(url_for('index'))

            # figure out who the user is
            resp = blueprint.session.get('/oauth2/v1/userinfo?alt=json')

            if resp.ok:
                userinfo = resp.json()
                user_data = dict(email=userinfo['email'], name=userinfo['name'],
                                 avatar=userinfo['picture'], google_id=userinfo['id'])
                user_obj = this.db.User.filter_by(email=user_data['email']).first()
                if user_obj is None:
                    flash(f"Access denied: {userinfo['email']} - contact admin!")
                    return redirect(url_for('index'))

                user_obj.avatar = userinfo['picture']
                user_obj.google_id = userinfo['id']
                this.db.commit()

                login_user(user_obj, remember=True)
                flash('Successfully signed in with Google', 'success')
            else:
                flash(f"Failed to fetch user info from {blueprint.name}", 'danger')

            next_url = session.pop('next_url', None)
            return redirect(next_url or url_for('index'))
