class _Test(object):
    def __init__(self, target):  # func==test函数
        print('test init')
        print(target)

    def __call__(self, func, *args, **kwargs):  # f为test函数的入参
        print('装饰器中的功能')
        return func

def Test(target):
    return _Test(target)

@Test('os')
def test(p):
    print(p)
    print('this is test func')

test('49494')
# def Test(func,**kwargs):
#     print(func)
#     print(kwargs)
#     return _Test(func)
#
# class _Test(object):
#     def __init__(self, func):
#         print('test init')
#         print('func name is %s ' % func)
#         self.__func = func
#     def __call__(self, func,*args, **kwargs):
#         print('装饰器中的功能')
#         print(func)
#         return func
#
# @Test('os')
# def test():
#     print('this is test func')
# test()
