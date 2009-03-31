class meta(type):
    def __init__(cls, cls_name, cls_bases, cls_dict):
        print 'hello, world'

class tst:
    __metaclass__ = meta

    def hi(self):
        """
        this is a docstring
        """
        print 'hello, world 2'

tst().hi()

print \
      "hello, world" \
      "how do you do?"

"asdf" + \
       str(5)
