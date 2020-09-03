import re

class WXSS:
    def __init__(self):
        self.template=open(r'E:\PycharmProjects\pgtool\WxTool\template\index.wxss','r')
        self.content=self.template.read()
        self.prog=re.compile('\.\w+')
        self.parsedir={}
        self.parse()

    def parse(self):
        m=self.prog.search(self.content)
        while m:
            self.parsedir[m.group()]=m.span()
            m=self.prog.search(self.content,m.end())

