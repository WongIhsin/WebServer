### 这是一些说明文档

---

#### 基本概念

**ORM**：Object Relational Mapping对象关系映射
即把关系数据库的一行映射为一个对象，一个类对应一个表
此时可能需要用到MetaClass

ORM框架下，类只能动态定义，使用使用的时候，才能够根据表的结构来定义出对应的类。使用的时候只需要如下操作：

```python
class User(Model):
    id = IntegerField('id')
    name = StringField('username')
    email = StringField('email')
    password = StringField('password')
    
u = User(id=12345, name='Ihsin', email='xx@xx.com', password='pwd')
u.save()
```

其他实现由ORM框架来提供

---

#### WSGI

Web Server Gateway Interface，Python提供的一个基础接口，只要求实现一个函数

```python
"""hello.py"""
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    # return [b'<h1>Hello, web!</h1>']
    body = '<h1>Hello, %s!</h1>' % (environ['PATH_INFO'][1:] or 'web')
    return [body.encode('utf-8')]
```

`environ`：一个包含所有HTTP请求信息的dict对象
`start_response`：一个发送HTTP响应的函数

```python
"""server.py"""
from wsgiref.simple_server import make_server
from hello import application

httpd = make_server('', 8000, application)
print('Serving HTTP on port 8000...')
httpd.serve_forever()
```

---

#### Flask

一个比较流行的Web框架

```python
"""app.py"""
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return '<h1>Home</h1>'

@app.route('/signin', methods=['GET'])
def signin_form():
    return '''<form action="/signin" method="post">
              <p><input name="username"></p>
              <p><input name="password" type="password"></p>
              <p><button type="submit">Sign In</button></p>
              </form>'''

@app.route('/signin', methods=['POST'])
def signin():
    if request.form['username'] == 'admin' and request.form['password'] == 'password':
        return '<h3>Hello, admin!</h3>'
    return '<h3>Bad username or password.</h3>'

if __name__ == '__main__':
    app.run()
```

模板技术，MVC模式，Flask默认支持jinja2

```python
"""app_with_template.py"""
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        return render_template('signin-ok.html', username=username)
    return render_template('form.html', message='Bad username or password', username=username)

if __name__ == '__main__':
    app.run()
```

home.html

```html
<html>
<head>
    <title>Home</title>
</head>
<body>
<h1 style="font-style:italic">Home</h1>
</body>
</html>
```

form.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Please Sign In</title>
</head>
<body>
{% if message %}
<p style="color:red">{{ message }}</p>
{% endif %}
<form action="/signin" method="post">
    <legend>Please sign in:</legend>
    <p><input name="username" placeholder="Username" value="{{ username }}"></p>
    <p><input name="password" placeholder="Password" type="password"></p>
    <p><button type="submit">Sign In</button></p>
</form>
</body>
</html>
```

signin-ok.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome, {{ username }}</title>
</head>
<body>
<p>Welcome, {{ username }}!</p>
</body>
</html>
```

---

#### aiohttp

aiohttp是基于asyncio实现的HTTP框架，支持百万高并发，异步IO

```python
"""server.py"""
import asyncio
from aiohttp import web

async def index(request):
    await asyncio.sleep(0.5)
    return web.Response(body=b'<h1>Index</h1>')

async def hello(request):
    await asyncio.sleep(0.5)
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'))

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server started at http://127.0.0.1:8000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
```

aiohttp的初始化函数init()也是一个coroutine，`loop.create_server()`则利用asyncio创建TCP服务

---

#### 廖雪峰实战

1. ***基本的app.py骨架***

   ```python
   """app.py"""
   import logging
   import asyncio, os, json, time
   from datetime import datetime
   from aiohttp import web
   
   logging.basicConfig(level=logging.INFO)
   
   def index(request):
       return web.Response(body=b'<h1>Awesome</h1>')
   
   @asyncio.coroutine
   def init(loop):
       app = web.Application(loop=loop)
       app.router.add_route('GET', '/', index)
       srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
       logging.info('Server started at http://127.0.0.1:9000...')
       return srv
   
   loop = asyncio.get_event_loop()
   loop.run_until_complete(init(loop))
   loop.run_forever()
   ```

   异步编程的一个原则：一旦决定使用异步，则系统每一层都必须是异步。

2. ***编写ORM***
   使用aiomysql为MySQL数据库提供了异步IO的驱动

   1. 创建连接池
      连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务

      ```python
      """orm.py"""
      import logging
      import asyncio
      import aiomysql
      
      async def create_pool(loop, **kw):
          logging.info('create database connection pool...')
          global __pool
          __pool = await aiomysql.create_pool(
              host=kw.get('host', 'localhost'),
              port=kw.get('port', 3306),
              user=kw['user'],
              password=kw['password'],
              db=kw['db'],
              charset=kw.get('charset', 'utf8'),
              autocommit=kw.get('autocommit', True),
              maxsize=kw.get('maxsize', 10),
              minsize=kw.get('minsize', 1),
              loop=loop
          )
      ```

   2. Select

      ```python
      # select
      # async里面调用一个子协程，并直接获得子协程的返回结果
      async def select(sql, args, size=None):
          log(sql, args)
          global __pool
          async with __pool.get() as conn:
              async with conn.cursor(aiomysql.DictCursor) as cur:
                  await cur.execute(sql.replace('?', '%s'), args or ())
                  if size:
                      rs = await cur.fetchmany(size)
                  else:
                      rs = await cur.fetchall()
              logging.info('rows returned: %s' % len(rs))
              return rs
      ```

   3. Insert，Update，Delete

      ```python
      # insert, update, delete
      async def execute(sql, args, autocommit=True):
          log(sql)
          async with __pool.get() as conn:
              if not autocommit:
                  await conn.begin()
              try:
                  async with conn.cursor(aiomysql.DictCursor) as cur:
                      await cur.execute(sql.replace('?', '%s'), args)
                      affected = cur.rowcount
                  if not autocommit:
                      await conn.commit()
              except BaseException as e:
                  if not autocommit:
                      await conn.rollback()
                  raise 
              return affected
      ```

   4. ORM
      设计ORM需要从上层调用者角度来设计
      首先是如何定义一个User对象，然后把数据库表User和它关联起来

      ```python
      from orm import Model, StringField, IntegerField
      
      class User(Model):
          __table__ = 'users'
          id = IntegerField(primary_key=True)
          name = StringField()
          
      # 创建实例
      user = User(id=123, name='Ihsin')
      user.insert()
      users = User.findAll()
      ```

      详见LearningRoute/Web/ORM.md

3. 编写***Model***
   
4. 





