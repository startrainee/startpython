from start.app.handlers.webframe import get
from start.app.model.User import User


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
