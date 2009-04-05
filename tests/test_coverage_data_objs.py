
class Test_Subtract(object):
    def setup(self):
        from figleaf.internals import CoverageData

        x = CoverageData()
        x.common = dict(foo = set([1, 2, 3]))

        y = CoverageData()
        y.common = dict(foo = set([1, 4]))

        self.x = x
        self.y = y

    def test_subtract_x_y(self):
        x, y = self.x, self.y
        
        z = x - y
        
        assert 'foo' in z.common
        assert z.common['foo'] == set([2, 3])

    def test_subtract_x_x(self):
        x, y = self.x, self.y
        
        z = x - x
        assert not z

    def test_subtract_y_x(self):
        x, y = self.x, self.y
        
        z = y - x
        assert 'foo' in z.common
        assert z.common['foo'] == set([4])

class Test_Add(object):
    def setup(self):
        from figleaf.internals import CoverageData

        x = CoverageData()
        x.common = dict(foo = set([1, 2, 3]))

        y = CoverageData()
        y.common = dict(foo = set([1, 4]))

        self.x = x
        self.y = y

    def test_add_x_y(self):
        x, y = self.x, self.y
        
        z = x + y
        
        assert 'foo' in z.common
        assert z.common['foo'] == set([1, 2, 3, 4])

    def test_add_x_x(self):
        x, y = self.x, self.y
        
        z = x + x

        assert 'foo' in z.common
        assert z.common['foo'] == set([1, 2, 3])

    def test_add_y_x(self):
        x, y = self.x, self.y
        
        z = y + x
        
        assert 'foo' in z.common
        assert z.common['foo'] == set([1, 2, 3, 4])
