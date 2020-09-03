import re
from string import Template

from pgtool.SqlTool.settings import databases
from pgtool.SqlTool.models.columns import build_col
from functools import lru_cache
from typing import Callable

class BaseClient:
    @classmethod
    def column_to_list(cls,column:str)->list:
        '''

        :param column: SELECT语句中的字段部分
        :return:把字段内容拆分存入列表
        '''

        column_list=column.replace('\n','').replace('\t','').replace(' ','').split(',')
        try:
            column_list=list(map(lambda x: x[x.index('.') + 1:], column_list))
        except ValueError:
            pass

        return column_list

    @classmethod
    def column_to_str(cls,column:list,sep=',')->str:
        return f'\n{sep}'.join(column)

    @classmethod
    def column_add_pre(cls,column,pre):
        column_list=cls.column_to_list(column)
        column_list=list(map(lambda x:f'{pre}.{x}',column_list))
        print(cls.column_to_str(column_list))
        return cls.column_to_str(column_list)
    @classmethod
    def column_add_quotes(cls,column):
        column_list = cls.column_to_list(column)
        column_list = list(map(lambda x: f"'{x}'", column_list))
        print(cls.column_to_str(column_list))
        return cls.column_to_str(column_list)

    @classmethod
    def column_map(cls,column,func,sep=','):
        column_list = cls.column_to_list(column)
        column_list=list(map(func,column_list))
        print(cls.column_to_str(column_list,sep=sep))
        return cls.column_to_str(column_list,sep=sep)
    @classmethod
    def column_from_create(cls,create:str)->list:
        #从建表语句中提取字段
        start=create.index('(')+1
        end=create.rindex(')')
        column=create[start:end]
        r=re.compile('.+,',re.I)
        m=r.search(column)
        column_list=[]
        while m:
            value=m.group()
            column_list.append(value.strip().split(' ')[0])
            m=r.search(column,m.end())
        return column_list

class SQLClient(BaseClient):
    def __init__(self,database='GP_STORE_DEV'):
        if database not in databases:            
            raise KeyError('该数据库没有做配置')

        self.conninfo=databases[database]
        
        if self.conninfo['TYPE']=='MSSQL':
            from pgtool.SqlTool.SQL.mssql import mssql_client
            self.conn=mssql_client(self.conninfo).conn
        elif self.conninfo['TYPE']=='Oracle':
            from pgtool.SqlTool.SQL.oracle import oracle_client
            self.client=oracle_client()
            self.conn=self.client.conn
        elif self.conninfo['TYPE']=='MySQL':
            from pgtool.SqlTool.SQL.mysql import mysql_client
            self.client=mysql_client(self.conninfo)
            self.conn=self.client.conn
            
        self.Rulefile=self.conninfo.get('RULEFILE')
        self.name=database
    def __str__(self):
        """返回sqlalchemy需要的连接字符串"""
        return self.client.__str__()

    def column(self,tablename,mode:int=1):
        """返回字段

        :parameter mode
            1-只返回字段名称列表
            2-以字典的形式返回sqlalchemy需要字段名称和字段类型
            3-以字典的形式返回字段名称和字段类型
        """
        return self.client.column(tablename,mode)
    def create(self,tablename:str,column:str=None):
        """返回建表语句
        :column 建表语句中的字段
        """
        return self.client.create(tablename,column)

    def select(self,tablename:str,add_columns:list=None):
        """select一张表，并列出该表所有字段"""
        return self.client.select(tablename,add_columns)

    def insert(self,totable:str,fromtable:str=None,align:bool=False,add_columns:list=None):
        """返回一条完整的insert语句

        :parameter align 自动对齐insert和select的字段，无法对齐的字段放置在后面
        """
        return self.client.insert(totable,fromtable,align,add_columns)

    def values(self,table):
        """提取table数据，返回一个生成器,生成器将以values的形式返回table数据(目前最多可返回10000条数据)"""
        return self.client.values(table)

    def table(self,db:str=None):
        """返回该db比较重要的表(剔除备份表、临时表)"""
        return self.client.table(db)

    def procedure(self,sp_name:str,*args:str):
        """返回存储过程创建语句"""
        return self.client.procedure(sp_name,*args)

    def batch(self,func:Callable,*args:str):
        """批量执行create或procedure语句"""
        return self.client.batch(func,*args)



class CREATE:
    def __init__(self,tablename,istemp=False,*col,**kwcols):
        self.columns = []

        for bc in col:
            coltype=eval(f"build_col['{bc}'].__str__()")
            self.columns.append(f"{bc} {coltype}")
        for k,v in kwcols.items():
            self.columns.append(f"{k} {v.__str__()}")

        self.istemp=istemp
        columns='\n,'.join(self.columns)
        self.sql=f"CREATE TABLE {tablename}(" \
               f"\n {columns})"

    def add_columns(self,column):
        if type(column)==str:
            self.columns.append(column)
        elif type(column)==list:
            self.columns.extend(column)

    @lru_cache
    def to_mysql(self):
        from pgtool.SqlTool.datatypes import INT,STR
        sql=self.sql
        if self.istemp:
            sql=sql.replace('TABLE','TEMPORARY TABLE')
        s=Template(sql)
        return s.substitute(STR=STR(),INT=INT())

    @classmethod
    def column(cls,sql:str):
        """从建表语句中提取字段信息"""
        sql=sql[sql.index('(')+1:sql.rfind(')')]
        sql=sql.split(',')
        sql=list(map(lambda x:x.strip(),sql))
        sql= list(map(lambda x: re.findall(r'(.+?) ', x)[0], sql))
        return ',\n'.join(sql)



    


