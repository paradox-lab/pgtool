import cx_Oracle
from string import Template
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class oracle_base:
    @classmethod
    def fetch_bulk_into(cls,**kwargs):
        '''

        :param kwargs:
            totablename,cursql
        :return:
        '''
        template=''
        with open(os.path.join(BASE_DIR,'theme','fetch_bulk_into.sql'),encoding='utf8') as file:
            for line in file:
                template+=line
        T=Template(template)
        return  T.safe_substitute(**kwargs)

class oracle_client:
    def __init__(self):
        self.conn = cx_Oracle.connect('d_insight/dinsight1306@DINSIGHT')

    def __str__(self):
        return 'oracle+cx_oracle://d_insight:dinsight1306@DINSIGHT'

    def close(self):
        self.conn.close()

    def cursor(self):
        return self.conn.cursor()

    def column(self,tablename,mode=1,quotechar=False):
        cur = self.conn.cursor()
        if mode==1:
            sql = f" select COLUMN_NAME from user_tab_columns where table_name='{tablename.upper()}'"
            cur.execute(sql)
            columns = []
            for row in cur.fetchall():
                columns.append(row[0])

            if quotechar:
                columns = list(map(lambda x: f"'{x}'", columns))

        elif mode==2:
            from sqlalchemy import types
            sql = f" select COLUMN_NAME,DATA_TYPE,DATA_LENGTH,DATA_PRECISION,DATA_SCALE from user_tab_columns where table_name='{tablename.upper()}'"
            cur.execute(sql)
            columns={}
            for COLUMN_NAME,DATA_TYPE,DATA_LENGTH,DATA_PRECISION,DATA_SCALE in cur.fetchall():
                if DATA_TYPE=='VARCHAR2':
                    columns[COLUMN_NAME]=types.VARCHAR(DATA_LENGTH)
                elif DATA_TYPE=='NVARCHAR2':
                    columns[COLUMN_NAME] = types.NVARCHAR()
                elif DATA_TYPE=='CHAR':
                    columns[COLUMN_NAME] = types.CHAR
                elif DATA_TYPE=='DATE':
                    columns[COLUMN_NAME] = types.DateTime()
                elif DATA_TYPE=='NUMBER':
                    if DATA_SCALE is not None:
                        columns[COLUMN_NAME]=types.FLOAT(DATA_SCALE)
                    else :
                        columns[COLUMN_NAME] = types.INT
                else:
                    #TODO 抛出异常，不识别的类型，需要继续补充if判断
                    pass

        cur.close()
        return columns

    def create(self,tablename):
        with self.conn.cursor() as cur:
            sql=f"select dbms_metadata.get_ddl('TABLE','{tablename.upper()}') from dual"
            cur.execute(sql)
            s=cur.fetchone()[0]
        return s.read()

    def procedure(self,sp_name):
        with self.conn.cursor() as cur:
            sql=f"select dbms_metadata.get_ddl('PROCEDURE','{sp_name.upper()}') from dual"
            cur.execute(sql)
            s=cur.fetchone()[0]
        return s.read()

    def package(self,pk_name):
        pass

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


    def batch(self,func,*args):
        result=[]
        for arg in args:
            result.append(func(arg))
        return result