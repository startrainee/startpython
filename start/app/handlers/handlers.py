import hashlib
import json
import logging
import re
import time

from aiohttp import web

from start.app.config.config import configs
from start.app.handlers.apis import APIValueError, APIError
from start.app.handlers.webframe import get, post
from start.app.model.User import User
from start.app.model.Blog import Blog
from start.app.model.orm import next_id

_RE_EMAIL = re.compile(r'^[a-z0-9.\-_]+@[a-z0-9\-_]+(\.[a-z0-9\-_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
COOKIE_NAME = "cookie_name"
_COOKIE_KEY = configs.session.secret


@get('/hello/{name}')
async def hello(name, request):
    print("hello ->>>>>>>>>>>>>>")
    print(request)
    print(type(request))
    return {
        '__template__': 'home.html',
        'name': name
    }


@get('/blogs')
def blogs(request):
    summary = 'When you close your eyes, the day will be night.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/login')
def login(request):
    return {
        '__template__': 'login.html',
    }


@get('/register')
def blogs(request):
    return {
        '__template__': 'register.html'
    }


@post('/api/users')
async def user_register(*, name, email, passwd):
    if not name or not name.strip():
        raise APIValueError(name)
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError(email)
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError(passwd)
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError(error='register:failed', data='email', message='该邮箱已被注册.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    res = await user.save()
    if res == 1:
        return res
    else:
        logging.error(msg="用户注册失败")
        raise APIError(error='register:failed', data='', message='系统错误，请稍后重试。')


@post('/api/authenticate')
async def authenticate(*, email, password):
    if not email or not _RE_EMAIL.match(email):
        logging.error("email")
        raise APIValueError(field=email)
    if not password:
        raise APIValueError(password, message="用户名密码验证错误。")
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIError('authenticate:failed', 'email', '该邮箱未注册。')
    # check passwd:
    user = users[0]
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError(password, message="用户名或者密码不正确。")

    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly="True")
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


# 计算加密cookie:
def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    mes = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(mes)


# 解密cookie:
async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        mes = cookie_str.split('-')
        if len(mes) != 3:
            return None
        uid, expires, sha1 = mes
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
async def index(request):
    print("index ->>>>>>>>>>>>>>")
    print(request)
    print(type(request))
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }


@get('/error')
async def error(request):
    print("index ->>>>>>>>>>>>>>")
    return 404


@get('/error1')
async def error1(request):
    print("index ->>>>>>>>>>>>>>")
    return 404, "出错了！！"
