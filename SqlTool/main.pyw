from tkinter import *
from tkinter.ttk import Combobox,Button,Treeview
from tkinter import filedialog
from tkinter import messagebox

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from inspect import getfullargspec

from pgtool.SqlTool.settings import databases
from pgtool import SQLClient
import typing

class Application(Tk):
    def __init__(self):
        '''初始化'''
        super().__init__() # 有点相当于tk.Tk()
        
        self.createWidgets()

    def createWidgets(self):
        '''界面'''
        self.title('SQL Tool - V1[LastUpdate2020-06-21]')
        self.columnconfigure(0, minsize=100)
        self.geometry("900x600")
        
        # 定义一些变量
        self.entryvar = StringVar()
        self.keyvar = StringVar()
        self.keyvar.set('RCS')
        #项目列表
        items = list(databases.keys())

        # 先定义顶部和内容两个Frame，用来放置下面的部件
        #导航栏
        topframe = Frame(self, height=50,width=800,bg="red")
        topframe.pack(side=TOP)
        #中间位置的frame
        middleframe = Frame(self,height=400,width=800)
        leftlabelframe=LabelFrame(middleframe,height=400,width=100,background="green")
        rightframe=Frame(middleframe,height=400,width=700,bg="blue")
        leftlabelframe.pack(side=LEFT)
        rightframe.pack(side=LEFT)
        middleframe.pack(side=TOP)

        #工具栏
        Bbatch=Button(leftlabelframe, text='batch', command=lambda :self.__buttonCB('batch'))
        Bbatch.pack(side=TOP,padx=3,pady=3)
        Bcreate = Button(leftlabelframe, text='create', command=lambda :self.__buttonCB('create'))
        Bcreate.pack(side=TOP, padx=3, pady=3)
        Binsert = Button(leftlabelframe, text='insert', command=lambda :self.__buttonCB('insert'))
        Binsert.pack(side=TOP, padx=3, pady=3)
        Bprocedure=Button(leftlabelframe, text='procedure', command=lambda :self.__buttonCB('procedure'))
        Bprocedure.pack(side=TOP, padx=3, pady=3)
        Bselect=Button(leftlabelframe, text='select', command=lambda :self.__buttonCB('select'))
        Bselect.pack(side=TOP, padx=3, pady=3)
        Btable=Button(leftlabelframe, text='table', command=lambda :self.__buttonCB('table'))
        Btable.pack(side=TOP, padx=3, pady=3)

        # 顶部区域（四个部件）
        # -- 前三个直接用 tk 的 widgets，第四个下拉列表 tk 没有，ttk 才有，比较麻烦
        glabel = Label(topframe, text='命令:')
        glabel2= Label(topframe, text='项目名称:')
        gentry = Entry(topframe, textvariable=self.entryvar)
        #对应命令行按钮
        glbutton= Button(topframe, command=self.__executecmd, text='调用方法')
        #对应测试连接按钮
        gbutton = Button(topframe, command=self.__testconn, text='测试连接')
        gcombobox = Combobox(topframe, values=items, textvariable=self.keyvar)
        # -- 绑定事件
        gentry.bind('<Return>', func=self.__executecmd)
        # -- 放置位置
        glabel.grid(row=0, column=0, sticky=W)        
        gentry.grid(row=0, column=1)
        glbutton.grid(row=0, column=2)
        glabel2.grid(row=0, column=3)
        gcombobox.grid(row=0, column=4)
        gbutton.grid(row=0, column=5)

        self.textbox = Text(rightframe,height=600,width=100)
        self.textbox.pack(side=LEFT, fill=BOTH,padx=5,pady=5)
        yscrollbar=Scrollbar(rightframe)
        yscrollbar.pack(side=RIGHT,fill=Y)
        yscrollbar.config(command=self.textbox.yview)
        self.textbox.config(yscrollcommand=yscrollbar.set)

    def __testconn(self,message_box=True):
        try:
            with SQLClient(self.keyvar.get()).conn:
                if message_box==True:
                    messagebox.showinfo('测试连接','连接成功')
            return True
        except AttributeError:
            SQLClient(self.keyvar.get()).conn.close()
            if message_box==True:
                messagebox.showinfo('测试连接','连接成功')
            return True
        except Exception as e:
            messagebox.showerror('测试连接',f'连接失败：{repr(e)}')
            print(repr(e))
            return False

    def __executecmd(self,event=None):
        
        def __execute():
            S=SQLClient(self.keyvar.get())
            arglist=[]
            for k,v in argsdict.items():
                try:
                    if v.get() =="":
                        value=None
                    elif isinstance(v,BooleanVar):
                        value=v.get()
                    elif k=="args":
                        arglist.append(f"*{v.get().split(',')}")
                        continue
                    elif k=="func":
                        value = f"S.{v.get()}"
                    elif v.get().startswith('[') and v.get().endswith(']'):
                        value = v.get()
                    elif isinstance(v,StringVar)==False:
                        value =v.get()
                    else:
                        value=f"'''{v.get()}'''"
                except Exception as e:
                    continue
                arglist.append(f"{value}")
                # arglist.append(f"{k}={value}")
            try:
                print(f"S.{text}({','.join(arglist)})")
                content=eval(f"S.{text}({','.join(arglist)})")
            except Exception as e:
                messagebox.showerror('错误', f'错误信息：{repr(e)}')
                return False
            if type(content)==str:
                self.textbox.delete('1.0',END)
                self.textbox.insert(END,content)
            elif isinstance(content,list):
                self.textbox.delete('1.0', END)
                self.textbox.insert(END,';\n--------------\n'.join(content))
            elif type(content)==dict:
                try:
                    self.tree.destroy()
                except AttributeError:
                    pass

                self.tree=Treeview(top,columns="备注",height=500)
                self.tree.column("备注",width = 300)
                self.tree.heading("#0",text="表名")
                self.tree.heading("#1",text="备注")
                for k,v in content.items():
                    self.tree.insert("", index=END, text=k, value=v)

                self.tree.pack()

        if self.__testconn(message_box=False)==False:
            return
        
        text=self.entryvar.get()
        
        if hasattr(SQLClient,text)==False:
            messagebox.showerror('错误',f'SQLClient没有此方法')
        else:            
            args=getfullargspec(eval(f'SQLClient.{text}')).args
            defaults=getfullargspec(eval(f'SQLClient.{text}')).defaults
            defaults=list(defaults) if defaults else []
            varargs=getfullargspec(eval(f'SQLClient.{text}')).varargs

            argstype = getfullargspec(eval(f'SQLClient.{text}')).annotations

            args.remove('self')
            for i in range(len(args)-len(defaults)):
                defaults.insert(0,None)

            top=Toplevel(self,height=800,width=600)
            top.title(f"方法名:{text}")
            Button(top, command=__execute, text='执行').pack()
            labFrame=LabelFrame(top,text="参数传递")

            argsdict={}
            typedict={
                str:"StringVar",
                list:"StringVar",
                bool:"BooleanVar",
                typing.Callable:"StringVar"
            }

            for index,arg in enumerate(zip(args,defaults,argstype.values())):
                # arg=(参数名称，默认值，类型)
                Labeltext=f"""{arg[0]}({str(arg[2])})"""
                Label(labFrame,text=Labeltext).grid(row=index,column=0)

                value=arg[1]

                exec(f"argsdict.update({arg[0]}={typedict[arg[2]]}(value={value}))")
                Entry(labFrame, textvariable=eval(f"argsdict['{arg[0]}']")).grid(row=index,column=1)

            if varargs:
                argsdict.update(args=StringVar(value=None))

                Label(labFrame, text='args(*)').grid(row=index+1, column=0)
                Entry(labFrame, textvariable=argsdict['args']).grid(row=index+1, column=1)

            labFrame.pack(padx=10,pady=5,ipadx=5,ipady=5)                            
        
    def __buttonCB(self, text):
        self.entryvar.set(text)
        return self.__executecmd()

    def addmenu(self, Menu):
        '''添加菜单'''
        Menu(self)


class MyMenu():
    '''菜单类'''

    def __init__(self, root):
        '''初始化菜单'''
        self.menubar = Menu(root)  # 创建菜单栏
        self.master = root

        # 创建“文件”下拉菜单
        filemenu = Menu(self.menubar, tearoff=0)
        # filemenu.add_command(label="Code Database", command=self.export_frame)
        CBmenu=Menu(filemenu,tearoff=False)
        CBmenu.add_command(label="Oracle", command=self.cb_oracle)
        filemenu.add_cascade(label="Code Database",menu=CBmenu)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)

        # 创建“帮助”下拉菜单
        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="关于", command=self.help_about)

        # 将前面三个菜单加到菜单栏
        self.menubar.add_cascade(label="Tools", menu=filemenu)
        self.menubar.add_cascade(label="帮助", menu=helpmenu)

        # 最后再将菜单栏整个加到窗口 root
        root.config(menu=self.menubar)

    def cb_oracle(self):
        global top
        try:
            top.destroy()
        except:
            pass
        finally:
            top = Toplevel(self.master)

        # fms = {'red': 'cross', 'green': 'boat', 'blue': 'clock'}
        # for fmColor in fms:
        #     Frame(top, bg=fmColor, cursor=fms[fmColor],
        #           height=200, width=250).pack(side=LEFT)
        frame1=Frame(top, bg='red', cursor='cross',height=200, width=250)
        frame1.pack(side=LEFT)
        lb1=Listbox(frame1)

        for file in os.listdir(os.path.join(BASE_DIR,'theme\oracle')):
            lb1.insert(END,file)

        frame2=Frame(top, bg='green', cursor='boat',height=200, width=250)
        frame2.pack(side=LEFT)

        text=Text(frame2,height=50,width=120)
        text.pack(padx=5,pady=5)
        yscrollbar=Scrollbar(top)
        yscrollbar.pack(side=RIGHT,fill=Y)
        yscrollbar.config(command=text.yview)
        text.config(yscrollcommand=yscrollbar.set)

        def itemSelected(event):
            obj=event.widget
            index=obj.curselection()

            if not obj.get(index):
                return
            text['state'] = NORMAL
            text.delete(1.0,END)
            with open(os.path.join(BASE_DIR,'theme\oracle',obj.get(index)),encoding='utf8') as f:
                for l in f :
                    text.insert(END,l)
            text['state'] = DISABLED
        lb1.bind("<<ListboxSelect>>",itemSelected)
        lb1.pack(side=TOP, padx=5, pady=10)

    def help_about(self):
        messagebox.showinfo('关于', '\n verion 1.0 \n 感谢您的使用！ \n')  # 弹出消息提示框

if __name__ == '__main__':
    # 实例化Application
    app = Application()
    
##    # 添加菜单:
    app.addmenu(MyMenu)
    
    # 主消息循环:
    app.mainloop()
