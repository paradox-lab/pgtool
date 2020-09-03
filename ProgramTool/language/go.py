from string import Template
from pgtool.ProgramTool.transfer import dtypes
import re

class VAR:
    '''var一般用于定义全局变量,:=只能在函数内部使用'''
    def var_in_func(self,string,funcname=None,mode='a'):

        self.backup()
        if not string.startswith('var') and string.find(':=')==-1:
            raise ValueError('语法错误')
        if funcname is None:
            funcname='main'

        if mode=='a':
            start=string.rfind(':=')+2
            start=string[start:].index('\n')+2
            self.content=self.content[:start]+'\r\n\t'+string+self.content[start:]
        elif mode=='i':
            start,end=re.search(f'func {funcname}\(\) {{', self.content).span()
            self.content =self.content[:end]+'\r\n\t'+string+self.content[end:]

class GoClient(VAR):
    def __init__(self,file=None):
        self.file=file
        if not file:
            self.content='package main\n\nfunc main() {\n}'
        with open(file,encoding='utf-8') as f:
            self.content=f.read()
        self.bak_content=self.content

    @classmethod
    def helloword(cls):
        return 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hellow World!")\n}'

    def save(self,filename=None):
        if filename is None:
            filename=self.file
        with open(filename,'w') as f:
            f.write(self.content)

    def undo(self):
        self.content=self.bak_content

    def backup(self):
        self.bak_content = self.content

def timeNowFormat(format='yyyy-mm-dd hh24:mi:ss'):
    format=format.replace('yyyy','2006').replace('mm','01').replace('dd','02').replace('hh24','15').replace('mi','04')\
        .replace('ss','05')
    return f'time.Now().Format("{format}")'

def ASSIGNMENT(var,value):
    T=Template("${var}:=${value}")
    return T.substitute(var=var,value=value)

def FOR(init=None,condition=None,post=None,body=None):
    T=Template("""for ${init}; ${condition}; ${post}{"
               ${body}
               }""")
    return T.substitute(init=init,condition=condition,post=post,body=body)

def DEF(**kwargs):
    annotations=[]

    for k,v in kwargs.get('annotations').items():
        try:
            dtype=dtypes[v]['go'][0]
        except KeyError:
            dtype=k
        if k =='return':
            output = v
        else:
            annotations.append(f"{k} {dtype}")

    kwargs.update(annotations=','.join(annotations))

    T=Template("""func ${name}(${annotations}) (${output}) {
${body}
}        
    """)

    return T.safe_substitute(output=output,**kwargs)
