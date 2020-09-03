import pymysql
import pandas as pd
from threading import Thread,Lock
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
import openpyxl
import os
from pgtool.SqlTool.sql_client import BaseClient
from pgtool.SqlTool.Project import tableinfo
from pgtool.SqlTool.models.columns import build_col
import re
from sqlalchemy import types

class mysql_client(BaseClient):
    def __init__(self,conninfo):
        self.host=conninfo['HOST']
        self.user=conninfo['USER']
        self.password=conninfo['PASSWORD']
        self.db=conninfo['DB']
        self.port=3306
        if SSH:=conninfo.get('SSH'):
            import paramiko
            from sshtunnel import SSHTunnelForwarder
            server = SSHTunnelForwarder(ssh_address_or_host=SSH['ssh_address_or_host'],  # 指定SSH中间登录地址和端口号
                                        ssh_username=SSH['ssh_username'],  # 指定地址B的SSH登录用户名
                                        ssh_password=SSH['ssh_password'],  # 指定地址B的SSH登录密码
                                        local_bind_address=SSH['local_bind_address'],
                                        # 绑定本地地址A（默认127.0.0.1）及与B相通的端口（根据网络策略配置，若端口全放，则此行无需配置，使用默认即可）
                                        remote_bind_address=SSH['remote_bind_address']
                                        # 指定最终目标C地址，端口号为mysql默认端口号3306
                                        )
            server.start()
            self.port=server.local_bind_port
            self.host="127.0.0.1"

        self.conn=pymysql.connect(self.host,self.user,self.password,self.db[0],ssl={"":""},port=self.port)
        
    def close(self):
        self.conn.close()

    def __str__(self):
        return 'mysql+pymysql://{}:{}@{}'.format(self.user,self.password,self.host)

    def cursor(self):
        return self.conn.cursor()

    def column(self,tablename,mode=1):
        cur = self.conn.cursor()
        sql = f'desc {tablename}'
        cur.execute(sql)
        if mode==1:
            columns = []
            for row in cur.fetchall():
                columns.append(row[0])

        elif mode==2:

            columns = {}

            for row in cur.fetchall():
                colname,dtype=row[:2]
                if dtype.startswith('bigint'):
                    columns[colname] = types.BIGINT
                elif dtype=='datetime':
                    columns[colname] = types.DateTime()
                elif dtype=='date':
                    columns[colname] = types.DATE()
                elif dtype.startswith('varchar'):
                    columns[colname] = types.VARCHAR(length=dtype[8:-1])
                elif dtype.startswith('int'):
                    columns[colname] = types.INT
                elif dtype.startswith('tinyint'):
                    columns[colname] = types.SMALLINT
                elif dtype.startswith('decimal'):
                    precision, scale=dtype[8:-1].split(',')
                    columns[colname] = types.DECIMAL(precision,scale)
                elif dtype=='json':
                    columns[colname] = types.JSON
                elif dtype=='text':
                    columns[colname] = types.TEXT
                else:
                    print(colname,dtype)
        elif mode==3:
            columns={}
            for row in cur.fetchall():
                columns[row[0]]=row[1]
        cur.close()
        return columns

    def create(self,tablename,column=None):
        if column is not None:
            cur = self.conn.cursor()
            sql = f'desc {tablename}'
            cur.execute(sql)
            columndir = {}
            for row in cur.fetchall():
                columndir[row[0]]=row[1:]
            cur.close()
            def func(x):
                columnstr = f'`{x}` {columndir[x][0]}'
                if columndir[x][1] == 'YES':
                    columnstr += ' DEFAULT NULL'
                elif columndir[x][1] == 'NO':
                    columnstr += ' NOT NULL'
                return columnstr
            columnstr=self.column_map(column,func)
            sql='''create table tablename ({})'''.format(columnstr)
            print(sql)
            return sql

        else:
            with self.conn.cursor() as cur:
                sql=f'SHOW CREATE TABLE {tablename};'
                cur.execute(sql)
                s=cur.fetchone()[1]
        return s

    def procedure(self,sp_name):
        with self.conn.cursor() as cur:
            sql = f'SHOW CREATE PROCEDURE {sp_name};'
            cur.execute(sql)
            s=cur.fetchone()[2]
        return s

    def select(self,tablename,add_columns=None):

        string='select'

        columns=self.column(tablename)

        if add_columns:
            columns.extend(add_columns)

        string=string+'\t'+'\n\t,'.join(columns)+f'\nfrom {tablename}'
##        print(string)
        return string

    def insert(self,totable,fromtable=None,align=False,add_columns=None):
        tocollist=self.column(totable)

        columns='\t'+'\n\t,'.join(tocollist)
        string=f'''insert into {totable} (
{columns}
)
        '''
        if fromtable:
            fromcolist=self.column(fromtable)+add_columns if add_columns else self.column(fromtable)

            if align:
                tocolset = set(tocollist)
                fromcolset = set(fromcolist)
                allcollist = tocollist+list(tocolset.difference(fromcolset))
                newtocollist=sorted(list(tocolset.intersection(fromcolset)),key=allcollist.index)
                newfromcollist=sorted(list(tocolset.intersection(fromcolset)),key=allcollist.index)

                newtocollist.extend(list(set(tocolset).difference(newtocollist)))
                print(newfromcollist)
                newfromcollist.extend(list(set(fromcolset).difference(newfromcollist)))
                print(newfromcollist)

                sqlselect='select'+'\t'+'\n\t,'.join(newfromcollist)+f'\nfrom {fromtable}'
            else:
                sqlselect=self.select(fromtable,add_columns=add_columns)

            string+='\n'+sqlselect

            if len(self.column(totable)) != (len(self.column(fromtable)) + (len(add_columns) if add_columns else 0)):
                string+='\n 注意：insert列数和select列数不一致'
        return string

    def values(self,table):
        coltype = self.column(table, 2).values()
        cur=self.conn.cursor()
        cur.execute('''select * from {} limit 10000'''.format(table))

        def func(value,coltype):
            if value is None:
                return "\n\t%s",'Null'
            elif coltype==types.BIGINT or coltype==types.INT or coltype==types.SMALLINT or coltype==types.DECIMAL:
                return '\n\t%s',value
            else:
                if isinstance(value,str):
                    if value.find("'") !=-1:
                        return '\n\t"%s"', value
                return "\n\t'%s'",value

        while True:
            valuelist=[]
            for row in cur.fetchmany(3):
                rowfmt= list(map(lambda x,y: func(x,y), row,coltype))
                valuelist.append('({})'.format(','.join(list(map(lambda x: x[0], rowfmt)))%tuple(map(lambda x: x[1], rowfmt))))

            yield ','.join(valuelist)
            if cur.rownumber==cur.rowcount:
                break
        cur.close()
        # string ='({})'.format(','.join(valueslist))
        # return string

    def table(self,db=None):
        if db is None:
            db=self.db[0]
        return eval(f'tableinfo.{db}')

    def batch(self,func,*args):
        result=[]
        for arg in args:
            result.append(func(arg))
        return result

    def _sp_add_var(self,sourcecode,string):
        # print(sourcecode)
        start=sourcecode.rindex('DECLARE')
        if sourcecode[start:].find('BEGIN') !=-1:
            start = sourcecode.rindex('DECLARE',1,start)

        end = sourcecode[start:].index(';') + 1
        return sourcecode[:start+end]+'\r\n '+string+sourcecode[start+end:]

    def _sp_refresh_code(self,sourcecode):
        sp_name = re.findall(r'PROCEDURE `(\w+)`', sourcecode)[0]
        if not sp_name:
            raise Exception('创建备份存储过程失败')
        pre_code=re.sub(r'PROCEDURE `(\w+)`',f'PROCEDURE `pre_{sp_name}`',sourcecode)
        cur=self.conn.cursor()
        try:
            cur.execute(pre_code)
        except pymysql.err.OperationalError:
            #重新连接
            self.conn.ping()
        cur.execute(f"DROP procedure IF EXISTS `{sp_name}`;")
        cur.execute(sourcecode)
        cur.execute(f"DROP procedure IF EXISTS `pre_{sp_name}`;")
        cur.close()

    def _sp_get_info(self,sourcecode):

        spname=re.findall(r'PROCEDURE `(\w+)`', sourcecode)

        start=sourcecode.upper().index('DECLARE')

        if dstart:= (sourcecode[start:].find('BEGIN')) != -1:
            end=sourcecode.upper().index('END;', dstart+251)+4
        else:
            end = sourcecode[start:].index(';') + 1
        declare=sourcecode[start:end]
        logic=sourcecode[end:].strip()
        info={'spname':spname,
              'declare':declare,
              'logic':logic}
        mark={}
        prog=re.compile('##\w+ (begin|end)\*\*',re.S)
        m=prog.search(info['logic'])
        while m:
            mark[m.group()]=m.span()
            m = prog.search(info['logic'],m.end())
        return info,mark


class CREATE:
    def __init__(self,tablename,*col,istemp=False):
        self.columns = []

        for bc in col:
            coltype=eval(f"build_col['{bc}'].__str__()")
            self.columns.append(f"{bc} {coltype}")

        self.TEMPORARY = "TEMPORARY" if istemp else ""
        self.sql=f"CREATE {self.TEMPORARY} TABLE {tablename}(" \
               f"\n {','.join(self.columns)})"

    def add_columns(self,column):
        if type(column)==str:
            self.columns.append(column)
        elif type(column)==list:
            self.columns.extend(column)

    def tosql(self):
        return self.sql






        


