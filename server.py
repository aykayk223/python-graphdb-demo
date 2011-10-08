from bulbs.model import *
from bulbs.property import *
import tornado.ioloop
import tornado.web
import tornado.template

"""
    Sample Node
"""

class User(Node):
    element_type = "user"
    name = Property(String, nullable=False)


"""
    tornedo handlers
"""
class AddHandler(tornado.web.RequestHandler):
    def get(self):
        # add user
        User(name=self.get_argument("name","empty")).save()

        # redirect to root
        self.redirect("/")


class UserHandler(tornado.web.RequestHandler):
    def get(self,id = None):

        # get data
        user = User.get(id)
        friend = self.get_argument("friend","")

        # set friend if not aready friend and not myself
        if friend != "" and id != friend :
            if not friend in [str(n._id) for n in user.gremlin("v.out('friend')")] :
                Relationship.create(User.get(id),"friend",User.get(friend))
                Relationship.create(User.get(friend),"friend",User.get(id))

        # gremlin query
        f  = user.gremlin(
            "v.out('friend')"
            )

        ff = user.gremlin(
            "x = [v]; v.out('friend').aggregate(x).out('friend').except(x).uniqueObject"
            )

        # load template
        tpl = tornado.template.Loader("./").load("user.html")
        self.write(tpl.generate( myself=user, friends=f, ffriends=ff ))


class UsersHandler(tornado.web.RequestHandler):
    def get(self,id = None):
        # get users
        users = User.get_all()

        # load template
        tpl = tornado.template.Loader("./").load("users.html")
        self.write(tpl.generate( users=users ))


"""
    tornedo webserver
"""
application = tornado.web.Application([
    (r"/",                    UsersHandler),
    (r"/add",                 AddHandler),
    (r"/user/([^/]+)/?",      UserHandler),
])

if __name__ == "__main__":
    application.listen(8890)
    tornado.ioloop.IOLoop.instance().start()
