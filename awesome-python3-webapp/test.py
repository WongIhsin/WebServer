#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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
# loop.close()

#
# import inspect
#
#
# def func(a, c, b=1, *args, email, name, passwd):
#     pass
#
#
# for k, v in inspect.signature(func).parameters.items():
#     print(k, v, v.kind)
#
# func(1, **{'email':1,'name':1,'passwd':1})
