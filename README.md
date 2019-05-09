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

失败了，不知道JavaScript
后端不显示信息

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

   ```python
   """models.py"""
   import time, uuid
   from orm import Model, StringField, BooleanField, FloatField, TextField
   
   def next_id():
       return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
   
   class User(Model):
       __table__ = 'users'
       id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
       email = StringField(ddl='varchar(50)')
       passwd = StringField(ddl='varchar(50)')
       admin = BooleanField()
       name = StringField(ddl='varchar(50)')
       image = StringField(ddl='varchar(500)')
       created_at = FloatField(default=time.time)
   
   class Blog(Model):
       __table__ = 'blogs'
       id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
       user_id = StringField(ddl='varchar(50)')
       user_name = StringField(ddl='varchar(50)')
       user_image = StringField(ddl='varchar(500)')
       name = StringField(ddl='varchar(50)')
       summary = StringField(ddl='varchar(200)')
       content = TextField()
       created_at = FloatField(default=time.time)
   
   class Comment(Model):
       __table__ = 'comments'
       id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
       blog_id = StringField(ddl='varchar(50)')
       user_id = StringField(ddl='varchar(50)')
       user_name = StringField(ddl='varchar(50)')
       user_image = StringField(ddl='varchar(500)')
       content = TextField()
       created_at = FloatField(default=time.time)
   ```

   然后初始化数据库

   此时要注意mysql***用户授权***设置问题，注意：先创建用户，然后用户名和IP要保持一致

   ```mysql
   mysql> create user 'www-data'@'localhost' identified by '1234';
   mysql> grant select, insert, update, delete on awesome.* to 'www-data'@'localhost';
   ```

   **`all privileges`**或者**`select, insert, update, delete`**等：表示将指定权限授予给用户；
   **`on`**：表示这些权限对哪些数据库和表生效，格式：数据库名.表名，这里*表示所有数据库，所有表
   **`to`**：将权限授予哪个用户。格式：“用户名”@“登录IP或域名”。%表示没有限制，在任何主机都能登录
   **`identified by`**：指定用户的登录密码（MySQL8.0.16版本时不可以在grant时候加）
   **`with grant option`**：表示允许用户将自己的权限授权给其他用户

4. ***建表语句***

   ```mysql
   create table users (
       `id` varchar(50) not null,
       `email` varchar(50) not null,
       `passwd` varchar(50) not null,
       `admin` bool not null,
       `name` varchar(50) not null,
       `image` varchar(500) not null,
       `created_at` real not null,
       unique key `idx_email` (`email`),
       key `idx_created_at` (`created_at`),
       primary key (`id`)
   ) engine=innodb default charset=utf8;
   
   create table blogs (
       `id` varchar(50) not null,
       `user_id` varchar(50) not null,
       `user_name` varchar(50) not null,
       `user_image` varchar(500) not null,
       `name` varchar(50) not null,
       `summary` varchar(200) not null,
       `content` mediumtext not null,
       `created_at` real not null,
       key `idx_created_at` (`created_at`),
       primary key (`id`)
   ) engine=innodb default charset=utf8;
   
   create table comments (
       `id` varchar(50) not null,
       `blog_id` varchar(50) not null,
       `user_id` varchar(50) not null,
       `user_name` varchar(50) not null,
       `user_image` varchar(500) not null,
       `content` mediumtext not null,
       `created_at` real not null,
       key `idx_created_at` (`created_at`),
       primary key (`id`)
   ) engine=innodb default charset=utf8;
   ```

5. 测试数据库是否可以使用

   ```python
   import orm
   from models import User, Blog, Comment
   import asyncio
   
   async def init(loop):
       await orm.create_pool(loop, user='www-data', password='1234', db='awesome')
       print('orm.create_pool Success')
       u = User(name='Test', email='test1@example.com', password='123', image='about:blank')
       await u.save()
   
   loop = asyncio.get_event_loop()
   loop.run_until_complete(asyncio.ensure_future(init(loop)))
   ```

6. ***使用装饰器定义@get和@post***

   ```python
   import functools
   
   def get(path):
       def decorator(func):
           @functools.wraps(func)
           def wrapper(*args, **kw):
               return func(*args, **kw)
           wrapper.__method__ = 'GET'
           wrapper.__method__ = path
           return wrapper
       return decorator
   ```

   装饰器：使用`import functools`

7. 需要使用RequestHandler类来封装URL处理函数
   RequestHandler类定义了`__call__()`方法，因此可以调用并视其为函数
   RequestHandler目的就是从URL函数中分析其需要接受的参数，从request中获取必要的参数，调用URL函数，然后把结果转换为web.Response对象

   ```python
   class RequestHandler(object):
       def __init__(self, app, fn):
           self._app = app
           self._func = fn
           self._has_request_arg = has_request_arg(fn)
           ...
           
       async def __call__(self, request):
           kw = ...
           try:
               r = await self._func(**kw)
               return r
           except APIError as e:
               return dict(error=e.error, data=e.data, message=e.message)
   ```

   这里需要创建一个方法`add_routes()`:
   首先通过包扫描，即python的`__import__`方法扫描到`add_route()`方法
   `add_route(app, fn)`实际上是将`fn`处理后通过`app.router.add_route(method, path, RequestHandler(app, fn))`添加URL处理函数映射关系
   其中的`RequestHandler()`实现了`__call__`方法，可以被当成函数一样调用
   RequestHandler其实是处理请求中的数据，取出数据然后执行对应方法

8. 初始化loop

   ```python
   async def init(loop):
       await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='www-data', password='1234', db='awesome')
       # 添加拦截器
       app = web.Application(loop=loop, middlewares=[
           logger_factory, response_factory
       ])
       # jinja2的初始化其实只是往app中的'__templating__'对象中添加了env对象
       init_jinja2(app, filters=dict(datetime=datetime_filter))
       # 添加URL处理方法映射
       add_routes(app, 'handlers')
       # 添加静态资源路径映射
       add_static(app)
       srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
       logging.info('server started at http://127.0.0.1:9000')
       return srv
   
   loop = asyncio.get_event_loop()
   loop.run_until_complete(init(loop))
   loop.run_forever()
   ```

   其中的`aiohttp.web.Application(loop=loop, middlewares=[...])`的`middlewares`是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的`middlewares`的处理
   其功能在于把通用的功能从每个URL处理函数中拿出来，集中放置到一个地方

9. 装配APP

   ```python
   """config_default.py"""
   
   configs = {
       'debug': True,
       'db': {
           'host': '127.0.0.1',
           'port': 3306,
           'user': 'www-data',
           'password': '1234',
           'db': 'awesome'
       },
       'session': {
           'secret': 'Awesome'
       }
   }
   ```

10. ***编写MVC***
    在handlers.py文件下编写URL处理函数，并在templates下创建相应的html文件

11. ***构建前端***
    jQuery是一个操作DOM的JavaScript库
    这里使用了CSS框架uikit
    没懂

12. 编写API

13. 用户注册和登录
    用户登录比用户注册困难，由于HTTP是一种无状态的协议，而服务器要跟踪用户状态，就只能通过cookie实现，大多数Web框架提供了Session功能来封装保持用户状态的cookie，Session的优点是简单易用，可以直接从Session中取出用户登录信息，Session的缺点是服务器需要在内存中维护一个映射表来存储用户登录信息，如果有两台以上服务器，就需要对Session做集群，因此，使用Session的Web App很难扩展。
    采用直接读取cookie的方式来验证用户登录，每次用户访问任意URL，都会对cookie进行验证，这种方式的好处是保证服务器处理任意的URL都是无状态的，可以扩展到多台服务器

    + 实现防伪造cookie使用单向算法SHA1
      当用户输入正确的口令登录成功之后，服务器可以从数据库取到用户的id，并按照如下方式计算出一个字符串
      `用户id + 过期时间 + SHA1（用户id + 用户口令 + 过期时间 + SecretKey）`
    + 当浏览器发送cookie到服务器端后，服务器端可以拿到的信息有：id，过期时间，SHA1值。如果未到过期时间，服务器就根据用户id查找用户口令，并计算`SHA1(用户id + 用户口令 + 过期时间 + SecretKey)`，并与浏览器cookie中的哈希进行比较，如果相等，则说明用户已登录，否则，cookie就是伪造的

14. **MVVM：Model View ViewModel**
    **Model**用纯JavaScript对象表示
    **View**是纯HTML
    把Model和View关联起来的是**ViewModel**
    ViewModel负责把Model的数据同步到View显示出来，还负责把View的修改同步回Model
    需要用JavaScript编写一个通用的ViewModel，这样，就可以复用整个MVVM模型了
    成熟的MVVM框架，AngularJS，KnockoutJS等，使用**Vue**来实现创建Blog的页面
    **双向绑定**

15. **日志列表页**

16. **部署App**



## JavaScript

貌似JavaScript可以再次发送小请求，如：/api/users

ajax javascript vue node.js

