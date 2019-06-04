import time

from model.orm import Model, StringField, BooleanField, FloatField, next_id


class User(Model):
    __table__ = 'users'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

# async def test(loop):
#    await orm.create_pool(loop=loop, user='subadmin', password='subadmin', db='test')
#    user = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
#    res = await user.save()
#    print(res)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test(loop))
