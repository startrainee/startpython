import hashlib
import json
import logging
import re
import time

from aiohttp import web

from config.config import configs
from handlers.apis import APIValueError, APIError, APIPermissionError, Page
from handlers.webframe import get, post
from model.User import User
from model.Blog import Blog
from model.orm import next_id

_RE_EMAIL = re.compile(r'^[a-z0-9.\-_]+@[a-z0-9\-_]+(\.[a-z0-9\-_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
COOKIE_NAME = "cookie_name"
_COOKIE_KEY = configs.session.secret


@post('/android_test_list')
async def android_test(request, *,email):
    users = await User.findAll('email=?', [email])
    r = web.Response()
    r.content_type = 'application/json'
    data = json.dumps(users)
    print(email)
    r.body = "{'message':'android_test_list'," \
             "'data:'" + str(data) + ",'code':200}"

    return r


@post('/android_test')
async def android_test_list(request, *, email):
    users = await User.findAll('email=?', [email])
    r = web.Response()
    r.content_type = 'application/json'
    data = json.dumps(users[0])
    print(email)
    r.body = "{'message':'android_test'," \
             "'data:'" + str(data) + ",'code':200}"

    return r


@get('/hello/{name}')
async def hello(name, request):
    print("hello ->>>>>>>>>>>>>>")
    print(request)
    print(type(request))
    return {
        '__template__': 'home.html',
        'name': name
    }


@get('/')
async def index(request):
    print("index ->>>>>>>>>>>>>>")
    users = await User.findAll()
    return {
        '__template__': '__test.html',
        'users': users
    }


@get('/blogs')
def blogs(request):
    summary = 'When you close your eyes, the day will be night.'
    blog_list = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blog_list
    }


@get('/login')
def login(request):
    return {
        '__template__': 'login.html',
    }


@get('/register')
def register(request):
    return {
        '__template__': 'register.html'
    }


# 博客编辑
@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

# 博客详情界面
@get('/blog/{blog_id}')
async def blog_detail_page(blog_id, request):
    blog = await blog_detail(blog_id, request)
    return {
        '__template__': 'mange_blog_detail.html',
        'users': blog
    }


def get_page_index(page):
    p = 1
    try:
        p = int(page)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

# 管理博客界面
@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


# 分页显示博客列表
@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/blog/{blog_id}')
async def blog_detail(blog_id, request):
    print("blog_detail() id:  %s" % blog_id)
    check_admin(request)
    blog_list = await Blog.findAll('id=?', [blog_id])
    blog = None
    if len(blog_list) > 0:
        blog = blog_list[0]

    print(blog)
    return blog


@post('/api/register')
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
        raise APIValueError("password", message="用户名或者密码不正确。")

    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly="True")
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


def check_admin(request):
    print("check_admin() request: " + str(request.__user__))
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    row = await blog.save()
    if row == 1:
        return blog
    raise APIError(error='api_create_blog:failed', data='', message='系统错误，请稍后重试。')


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


@get('/error')
async def error(request):
    print("error ->>>>>>>>>>>>>>")
    return 404


@get('/error1')
async def error1(request):
    print("error1 ->>>>>>>>>>>>>>")
    return 404, "出错了！！"
