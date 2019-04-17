import asyncio
import time
import uuid

from start.app.model.meta import orm
from start.app.model.meta.orm import Model, StringField, BooleanField, FloatField


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


async def test(loop):
    await orm.create_pool(loop=loop, user='subadmin', password='subadmin', db='test')
    user = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
    res = await user.save()
    print(res)


loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
