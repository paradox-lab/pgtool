from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *

from idlelib.percolator import Percolator
from idlelib.colorizer import color_config, ColorDelegator
from pgtool import colorizer
from string import Template
from pgtool.ProgramTool.keywords import dir_tab
from pgtool.ProgramTool.setting import themepath
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class NotebookWindow:
    def __init__(self):
        self.language=['py','go','java','bas','js','html','css','wxml','wxss','sql','oracle','mysql','mssql']
        self._generateWidget(*self.language)

    def get_current_Txt(self):
        lang = self.notebook.tab(self.notebook.select())['text']
        return eval(f'self.{lang}Txt')

    def _generateWidget(self,*args):
        script='''self.${arg}Frame=Frame(self.notebook)
self.${arg}Txt=ScrolledText(self.${arg}Frame,height=50,width=120,background="white")        
self.${arg}Txt.pack(padx=5,pady=5,fill=BOTH,expand=TRUE)      
self.${arg}Txt.pack(padx=5,pady=5,fill=BOTH,expand=TRUE)  
color_config(self.${arg}Txt)
p = Percolator(self.${arg}Txt)
d = colorizer.ColorDelegator('${arg}')
p.insertfilter(d)
self.${arg}Txt.bind("<Button-1>", self.TxtCallback)
        '''
        for arg in args:
            s=Template(script)
            exec(s.substitute(arg=arg))

    def TxtCallback(self,event):
        langTxt=self.get_current_Txt()
        self.LC.set(f"行列号：{langTxt.index(CURRENT)}")

    def _generate_Txt_data(self):

        script =r'''self.notebook.add(self.${lang}Frame, text='${lang}')
self.${lang}Txt['state'] = NORMAL
self.${lang}Txt.delete(1.0, END)
for mark_name in self.${lang}Txt.mark_names():
    self.${lang}Txt.mark_unset(mark_name)

mark_dict = {}    
marknamelist = []    
try:
    with open(os.path.join(themepath, self.var.get(), self.objcache, file)) as f:
        data=f.readlines()
except UnicodeDecodeError:
    with open(os.path.join(themepath, self.var.get(), self.objcache, file),encoding='utf8') as f:
        data=f.readlines()
        
for l in data:
    self.${lang}Txt.insert(END,l)            
    try:
        tab=dir_tab[lang]          
        if l.startswith(tab*3) and l.endswith('***\n'):
            tag_name = f"{l[3:-4]}"                    
            mark_dict[tag_name] = str(float(self.${lang}Txt.index(INSERT)) - 1)
            marknamelist.append(tag_name)
        # 小标题
        elif l.startswith(tab*2) and l.endswith('**\n'):
            tag_name = f"{l[2:-3]}({int(float(self.${lang}Txt.index(INSERT))) - 1})"
            mark_dict[tag_name] = str(float(self.${lang}Txt.index(INSERT)) - 1)
            marknamelist.append(tag_name)        

        #用于点击标签时定位到对应位置
        for tag_name, tag_index in mark_dict.items():
            self.${lang}Txt.mark_set(tag_name, tag_index)        
        self.marknamedict['${lang}']=marknamelist
                                
    except KeyError:
        continue

self.${lang}Txt['state'] = DISABLED    
    '''
        for file in os.listdir(os.path.join(themepath, self.var.get(), self.objcache)):
            if file.startswith(self.cbvarchache) and not file.endswith('.py'):
                lang = os.path.splitext(file)[1][1:]

                s=Template(script)

                exec(s.substitute(lang=lang))



