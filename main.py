"""
Entrypoint to flask application for tassaron's portfolio website
"""
import flask

#import os

app = flask.Flask(__name__)
#app.secret_key = os.urandom(16)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')

@app.route('/projects/')
def projectsBaseDir():
    return flask.redirect("https://rainey.tech", code=301)

@app.route('/projects/<projectName>')
def projects(projectName):
    if projectName == 'pyaudiovis':
        return flask.redirect("https://github.com/djfun/audio-visualizer-python/tree/feature-newgui", code=301)
    elif projectName == 'breakout':
        return flask.redirect("https://fun.tassaron.com/breakout", code=301)

"""
@app.route('/newpost', methods=['POST'])
@app.route('/blog')
"""

if __name__ == "__main__":
    app.run(debug=True)
