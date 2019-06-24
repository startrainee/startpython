from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/siginin', methods=['GET'])
def sign_in():
    return render_template('sigin_in.html')


@app.route('/siginin', methods=['POST'])
def signin():
    # 需要从request对象读取表单内容：
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        return render_template('sigin_ok.html')
    return render_template('sigin_in.html', message='Bad username or password', username=username)


if __name__ == '__main__':
    app.run()
