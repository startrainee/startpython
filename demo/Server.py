# 从wsgiref模块导入:
from wsgiref.simple_server import make_server
# 导入我们自己编写的application函数:

# 创建一个服务器，IP地址为空，端口是9998，处理函数是application:
from demo.Application import application

httpd = make_server('', 9998, application)
print('Serving HTTP on port 8000...')
# 开始监听HTTP请求:
httpd.serve_forever()
