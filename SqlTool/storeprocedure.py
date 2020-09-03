from idlelib.colorizer import any
from pgtool import SQLClient
from functools import wraps
import re

def make_pat():
    select = any('SELECT',["SELECT\\b\\s+\\b","FROM\\b\\s+\\b","\\b\\s+WHERE","[\\b\\s]?\)","[\\b\\s]?;"])
    update=any('UPDATE',["UPDATE\\b\\s+\\b","[\\b\\s]?SET"])
    insert=any('INSERT',["INSERT\\b\\s+INTO\\b\\s+","[\\b\\s]?\(","\\b\\s+SELECT","\\b\\s+VALUES"])
    return select+'|'+update+'|'+insert

prog=re.compile(make_pat(),re.I)

class SPUnitTest(SQLClient):
    '''
    第一步，测试用例指定测试的存储过程名称
    第二步，指定替换表并准备测试数据,值传入至修饰器，
    第三步，复制存储过程创建脚本，类修饰器根据指定的替换表，把脚本相关表替换为测试表

    '''

    def __init__(self,db,sp_name,target,copy_row=10000,sp_test='create'):
        '''

        :param db:
        :param sp_name:
        :param target:
        :param copy_row:
        :param sp_test:'exists'-在已有的测试存储过程上修改,'create'-创建新的测试存储过程
        '''
        SQLClient.__init__(self,db)

        self.sp_name=sp_name
        self.target = target
        self.copy_row=copy_row
        self.sp_test=sp_test
        if sp_test=='exists':
            self.sourcecode=self.procedure(f'test_{sp_name}')
        else:
            self.sourcecode=self.procedure(sp_name)
        self.prog=prog
        self.select_table=[]
        self.update_table=[]
        self.insert_table=[]

    def _test_table(self):
        sql=self.create(self.target).replace(self.target,f'test_{self.target}')
        return sql

    def _test_data(self):
        sql = f"""insert into test_{self.target}
                select * from {self.target} limit {self.copy_row};        
                """
        return sql

    def _test_sp(self):
        subsourcecode=self.sourcecode.replace(' '+self.target+' ',' test_'+self.target+' ').replace('\t' + self.target + ' ', ' test_' + self.target + ' ')
        if self.sp_test !='exists':
            subsourcecode=subsourcecode.replace('`'+self.sp_name+'`','`test_'+self.sp_name+'`')
        return subsourcecode

    def get_table(self):
        m = self.prog.search(self.sourcecode)
        while m:
            for key, value in m.groupdict().items():
                if value:
                    if key=='SELECT' and m.group().upper().startswith('FROM'):
                        s = m.span()[1]
                        m = self.prog.search(self.sourcecode, m.end())
                        e = m.span()[0]
                        table = self.sourcecode[s:e]
                        self.select_table += (table.split(','))
                    elif key=='UPDATE' and m.group().upper().startswith('UPDATE'):
                        s = m.span()[1]
                        m = self.prog.search(self.sourcecode, m.end())
                        e = m.span()[0]
                        table = self.sourcecode[s:e]
                        self.update_table += (table.split(','))
                    elif key=='INSERT' and m.group().upper().startswith('INSERT'):
                        s = m.span()[1]
                        m = self.prog.search(self.sourcecode, m.end())
                        e = m.span()[0]
                        table = self.sourcecode[s:e]
                        self.insert_table += (table.split(','))

            m = self.prog.search(self.sourcecode,m.end())
        self.select_table=list(set(list(map(lambda x:re.findall('\w+',x,re.I)[0],self.select_table))))
        self.update_table = list(set(list(map(lambda x: re.findall('\w+', x, re.I)[0], self.update_table))))
        self.inert_table = list(set(list(map(lambda x: re.findall('\w+', x, re.I)[0], self.insert_table))))
        return self.select_table,self.update_table,self.insert_table

    def __call__(self,func,*args, **kwargs):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            cur=self.conn.cursor()
            sql=self._test_table()
            #创建测试表
            cur.execute(sql)
            sql=self._test_data()
            #插入测试数据
            cur.execute(sql)
            self.conn.commit()
            sql=self._test_sp()
            #创建测试存储过程
            cur.execute(f"DROP procedure IF EXISTS `test_{self.sp_name}`;")
            cur.execute(sql)
            cur.close()
            self.conn.close()
            return func(*args, **kwargs)
        return wrapped_function

def patch(db,sp_name,target,copy_row=10000,sp_test='create'):
    return SPUnitTest(db,sp_name,target,copy_row=copy_row,sp_test=sp_test)

#'GP_STORE_DEV','SYNC_BPM_MASTER_BASIC_PROCESS_A_SELECTION','SYNC_BPM_MASTER_PRICE_COMBINATION','SYNC_BPM_MASTER_BASIC'
class StoreProcedure(SQLClient):
    def __init__(self,db,*args):
        SQLClient.__init__(self, db)
        self.splist=list(args)
        self.spsoucelist=list(map(lambda x:self.procedure(x),self.splist))
        self.spdir=dict(zip(self.splist,self.spsoucelist))
        self.bak_flag=True
        self.bak_spsoucelist=[]

    def add_var(self,string):
        '''增加变量语句'''
        self.spsoucelist = list(
            map(lambda x, y: self.client._sp_add_var(x, y), self.spsoucelist, [string for i in range(3)]))

    def add_after_string(self,index_string,add_string):
        '''在指定字符串下一行添加语句 格式为元组(指定的字符串，要添加的语句)'''
        def __add_script(x):
            start = x.index(index_string)
            return x[:start + len(index_string)] + '\r\n' + add_string + x[start + len(index_string):]
        self.spsoucelist = list(map(lambda x: __add_script(x), self.spsoucelist))

    def add_before_string(self,index_string,add_string):
        '''在指定字符串的前一行添加语句 格式为元组(指定的字符串，要添加的语句)'''
        def __add_script(x):
            start = x.index(index_string)
            return x[:start] + '\r\n' + add_string + '\r\n' + x[start:]

        self.spsoucelist = list(map(lambda x: __add_script(x), self.spsoucelist))

    def delete_line(self,string):
        '''删除代码语句'''
        delete_line = string.replace('(', '\(').replace(')', '\)')
        delete_line = delete_line + '\s*'
        func = lambda x: re.sub(delete_line, '', x, flags=re.I)
        self.spsoucelist = list(map(func, self.spsoucelist))

    def replace_line(self,old_str,new_str):
        '''替换代码语句 格式为元组(旧值,新值)'''
        func = lambda x: x.replace(old_str, new_str)
        self.spsoucelist = list(map(func, self.spsoucelist))

    def sp_undo(self):
        if not self.bak_spsoucelist:
            self.spsoucelist=self.bak_spsoucelist

    def backup(self):
        files=[]
        for spname, spsouce in self.spdir.items():
            with open('{}.sql'.format(spname), 'w') as bak_file:
                for line in spsouce.split('\n'):
                    bak_file.write(line)
            files.append('{}.sql'.format(spname))
        return files

    def sp_execute(self):
        #首次执行前先备份存储过程
        if self.bak_flag:
            self.backup()
            self.bak_flag=False

        self.bak_spsoucelist=self.spsoucelist
        for spsouce in self.spsoucelist:
            self.client._sp_refresh_code(spsouce)
            print('刷新成功',spsouce)

    def sp_get_info(self,sp_name):
        sourcecode=self.procedure(sp_name)
        return self.client._sp_get_info(sourcecode)

    @classmethod
    def sync_sp(cls,fromdb,todb,spname):
        S=SQLClient(fromdb)
        spcode=S.procedure(spname)
        conn = SQLClient(todb).conn
        cur=conn.cursor()
        cur.execute(f"DROP procedure IF EXISTS `{spname}`;")
        cur.execute(spcode)
        cur.close()
        S.conn.close()