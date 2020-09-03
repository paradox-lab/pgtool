from inspect import getfullargspec,getsource,ismodule
from pgtool.ProgramTool.language import go
import re

from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
import os
from idlelib.percolator import Percolator
from idlelib.colorizer import color_config, ColorDelegator
from pgtool import colorizer
from pgtool.ProgramTool.notebookwindow import NotebookWindow
from pgtool.ProgramTool.setting import themepath

class Application(Tk,NotebookWindow):
    def __init__(self,root=None):
        # super().__init__()  # 有点相当于tk.Tk()
        if root is None:
            root=Tk()

        self.parent=root
        self.createWidgets()

    def createWidgets(self):
        self.parent.title("ProgramTool")
        self.pw = PanedWindow(orient=HORIZONTAL)
        self.notebook = Notebook(self.parent)
        self.notebook.bind('<Button-1>',self.markname_show)
        self.notebook.bind('<Enter>',self.markname_show)
        NotebookWindow.__init__(self)

        leftframe=LabelFrame(self.pw,text="theme",width=120,height=150)
        self.pw.add(leftframe)

        self.var = StringVar(leftframe)
        self.varcache=""

        optionmenu = OptionMenu(leftframe, self.var, "后端", "后端", "前端","存储过程")
        optionmenu.pack(side=TOP,padx=1,pady=1)
        btn = Button(leftframe, text="切换", command=self.optionSelection)
        btn.pack(pady=1, anchor=S, side=TOP)

        self.LO=StringVar()

        self.LOlabel=Label(leftframe,textvariable=self.LO)
        self.LOlabel.pack(side=TOP,  pady=1)

        self.lb1=Listbox(leftframe,height=30)

        self.lb1.bind("<<ListboxSelect>>",self.itemSelected)
        self.lb1.pack(side=TOP, padx=1, pady=1)

        #目录
        rightframe=LabelFrame(self.pw,text="目录",width=120,height=150)
        self.pw.add(rightframe)

        self.LC=StringVar()

        self.LClabel=Label(rightframe,textvariable=self.LC)
        self.LClabel.pack(side=TOP, padx=1, pady=1)

        self.cbvar=StringVar()
        self.cbvarchache=''
        self.cb=Combobox(rightframe,textvariable=self.cbvar,value=('api','demo','function'))
        self.cb.current(0)
        self.cb.bind("<<ComboboxSelected>>", self.comboSelection)
        self.cb.pack(pady=1, anchor=S, side=TOP)

        self.lb2 = Listbox(rightframe,height=30,width=25)
        self.lb2.bind("<<ListboxSelect>>", self.markSelected)
        self.lb2.pack(side=TOP, padx=5, pady=10)

        self.marknamedict=dict(zip(self.language,[[] for x in self.language]))

        self.notebook.add(self.pyFrame,text="py")

        self.notebook.pack(padx=10,pady=10,fill=BOTH,expand=TRUE)

        self.pw.add(self.notebook)

        #######################
        self.pw.pack(fill=BOTH,expand=True,padx=10,pady=10)
        self.objcache=""
        self.optionSelection()
    def itemSelected(self,event):
        '''点击theme的事件'''
        obj = event.widget
        index = obj.curselection()
        if index == ():
            return
        self.objcache = obj.get(index)

        cbvalue=list(map(lambda x:os.path.splitext(x)[0],os.listdir(os.path.join(themepath,self.varcache,self.objcache))))
        cbvalue=list(set(cbvalue))
        self.cb['value']=cbvalue
        self.LO.set(self.objcache)
        self.pyTxt['state'] = NORMAL
        self.pyTxt.delete(1.0, END)
        self.comboSelection(None)
        self.markname_show(None)

    def markSelected(self,event):
        '''定位到对应标签的位置'''
        obj = event.widget
        index = obj.curselection()
        if index == ():
            return
        langTxt=self.get_current_Txt()
        langTxt.see(langTxt.index(obj.get(index)))

    def optionSelection(self,):
        '''切换theme'''
        if self.var.get()!=self.varcache:
            self.varcache=self.var.get()
            self.lb1.delete(0, END)
            self.lb2.delete(0,END)

            for file in os.listdir(os.path.join(themepath, self.varcache)):
                self.lb1.insert(END, file)
    def comboSelection(self,event):
        '''切换api,demo,function等'''
        # if self.cbvar.get() ==self.cbvarchache:
        #     return
        self.cbvarchache=self.cbvar.get()
        for i in range(len(self.notebook.tabs())):
            self.notebook.forget(0)
        if self.varcache=='后端':
            self.notebook.add(self.pyFrame, text="py")
            self.__pyText()

        self._generate_Txt_data()
    def __pyText(self):
        self.pyTxt['state'] = NORMAL
        self.pyTxt.delete(1.0, END)
        try:
            for mark_name in self.pyTxt.mark_names():
                self.pyTxt.mark_unset(mark_name)
            with open(os.path.join(themepath, self.varcache, self.objcache, f'{self.cbvarchache}.py'),
                      encoding='utf8') as f:
                mark_dict = {}
                marknamelist = []
                for l in f:
                    self.pyTxt.insert(END, l)
                    # 设置书签
                    # 大标题
                    if l.startswith('###') and l.endswith('***\n'):
                        tag_name = f"{l[3:-4]}"
                        mark_dict[tag_name] = str(float(self.pyTxt.index(INSERT)) - 1)
                        marknamelist.append(tag_name)
                    # 小标题
                    elif l.startswith('##') and l.endswith('**\n'):
                        tag_name = f"{l[2:-3]}({int(float(self.pyTxt.index(INSERT))) - 1})"
                        mark_dict[tag_name] = str(float(self.pyTxt.index(INSERT)) - 1)
                        marknamelist.append(tag_name)
                #用于点击标签时定位到对应位置
                for tag_name, tag_index in mark_dict.items():
                    self.pyTxt.mark_set(tag_name, tag_index)

                self.marknamedict['py']=marknamelist

        except FileNotFoundError:
            self.lb2.delete(0, END)

        self.pyTxt['state'] = DISABLED

    def markname_show(self,event):
        lang=self.notebook.tab(self.notebook.select())['text']
        self.lb2.delete(0, END)
        for mark_name in self.marknamedict[lang]:
            self.lb2.insert(END, mark_name)

class ProgramClient:
    def __init__(self,func,var=None,funpare=None):

        self.funparse=self.parse(func)

    @classmethod
    def parse(cls,func,var=None):

        funcparse={}
        fullargspec=getfullargspec(func)
        body=getsource(func).split('\n')[1:]
        while True:
            try:
                body.remove('')
            except ValueError:
                break

        body='\n'.join(body)

        funcparse.update(name=func.__name__,
                        args=fullargspec.args,
                        annotations=fullargspec.annotations,
                         varnames=func.__code__.co_varnames,
                         body=body
                         )
        return funcparse

    def to_go(self):
        return go.DEF(**self.funparse)


        
        
