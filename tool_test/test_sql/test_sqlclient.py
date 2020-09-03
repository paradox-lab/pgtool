import unittest
from pgtool import BaseClient,SQLClient
from pgtool.SqlTool.settings import databases


        ###########oracle
        # 需要连接VPN
#         cls.oracle = SQLClient('RCS')
#         cur2 = cls.oracle.conn.cursor()
#         #创建测试表
#         sql2 = '''create table test_SQLClient(
# test_varchar2 varchar2(50),
# test_nvachar2 nvachar2(20),
# test_char char(20),
# test_date date,
# test_tinyint tinyint(1),
# test_number number,
# test_number2 number(24,2)
# )'''
#         cur2.execute(sql2)
#         cur2.close()

# ORACLE
# cur2 = cls.oracle.conn.cursor()
# cur2.execute(sql)
# cur2.close()
# cls.oracle.conn.close()

colstr='''product_code\n,official_sos_date\n,rowversion\n,english_product_description\n,old_item_code_product_description\n,quality_guaranteed\n,base_unit_of_measure\n,old_barcode\n,item_barcode'''

collist=['product_code', 'official_sos_date', 'rowversion', 'english_product_description', 'old_item_code_product_description', 'quality_guaranteed', 'base_unit_of_measure', 'old_barcode', 'item_barcode']

class FunctionTest(unittest.TestCase):
    def test_column_to_list(self):
        self.assertEqual(BaseClient.column_to_list(colstr),collist)
    def test_column_to_str(self):
        self.assertEqual(BaseClient.column_to_str(collist),colstr)
    def test_column_add_pre(self):
        self.assertEqual(BaseClient.column_add_pre(colstr,'a'),'a.product_code\n,a.official_sos_date\n,a.rowversion\n,a.english_product_description\n,a.old_item_code_product_description\n,a.quality_guaranteed\n,a.base_unit_of_measure\n,a.old_barcode\n,a.item_barcode')
    def test_column_add_quotes(self):
        self.assertEqual(BaseClient.column_add_quotes(colstr),"'product_code'\n,'official_sos_date'\n,'rowversion'\n,'english_product_description'\n,'old_item_code_product_description'\n,'quality_guaranteed'\n,'base_unit_of_measure'\n,'old_barcode'\n,'item_barcode'")
    def test_column_map(self):
        self.assertEqual(BaseClient.column_map(colstr,lambda x:f"a.{x}=b.{x}"),'a.product_code=b.product_code\n,a.official_sos_date=b.official_sos_date\n,a.rowversion=b.rowversion\n,a.english_product_description=b.english_product_description\n,a.old_item_code_product_description=b.old_item_code_product_description\n,a.quality_guaranteed=b.quality_guaranteed\n,a.base_unit_of_measure=b.base_unit_of_measure\n,a.old_barcode=b.old_barcode\n,a.item_barcode=b.item_barcode')
    def test_column_from_create(self):
        sql = '''create table test_SQLClient(
        test_int int,
        test_varchar varchar(50),
        test_bigint bigint(20),
        test_datetime datetime,
        test_date date,
        test_tinyint tinyint(1),
        test_decimal decimal(20,2),
        test_json json,
        test_text text
        )'''
        self.assertEqual(BaseClient.column_from_create(sql),['test_int', 'test_varchar', 'test_bigint', 'test_datetime', 'test_date', 'test_tinyint', 'test_decimal', 'test_json'])

class SQLClientTestMysql(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.table='test_SQLClient'

        ############mysql
        cls.mysql=SQLClient('GP_STORE_DEV')
        cur1=cls.mysql.conn.cursor()
        # 创建测试表
        sql='''create table test_SQLClient(
test_int int,
test_varchar varchar(50),
test_bigint bigint(20),
test_datetime datetime,
test_date date,
test_tinyint tinyint(1),
test_decimal decimal(20,2),
test_json json,
test_text text
)'''
        cur1.execute(sql)
        cur1.execute("""insert into test_sqlclient values(123,'123',123456,'2020-09-02 07:36:27','2020-09-02',1,20.24,'{"a":"b"}','aabbcc')""")
        cls.mysql.conn.commit()

        sql='''CREATE DEFINER=`pgadmin`@`%` PROCEDURE `test_SQLClient`()\nBEGIN\r\n\tSELECT 1;\r\n\r\nEND'''
        cur1.execute(sql)
        cur1.close()

    @classmethod
    def tearDownClass(cls) -> None:
        cur1=cls.mysql.conn.cursor()
        sql = 'drop table if exists test_SQLClient'
        cur1.execute(sql)
        sql = 'drop procedure if exists test_SQLClient'
        cur1.execute(sql)
        cur1.close()
        cls.mysql.conn.close()

    def test_init(self):
        #TODO 测试实例化异常
        pass
    def test_str(self):
        info=databases['GP_STORE_DEV']
        value='mysql+pymysql://{}:{}@{}'.format(info['USER'],info['PASSWORD'],info['HOST'])
        self.assertEqual(self.mysql.client.__str__(),value)
        # self.assertEqual(self.oracle.client.__str__(),'oracle+cx_oracle://d_insight:dinsight1306@DINSIGHT')
    def test_coloumn(self):
        self.assertEqual(self.mysql.column(self.table),['test_int', 'test_varchar', 'test_bigint', 'test_datetime', 'test_date', 'test_tinyint', 'test_decimal', 'test_json','test_text'])
        from sqlalchemy import types
        self.assertEqual(str(self.mysql.column(self.table,2)),str({
            'test_int': types.INTEGER,
            'test_varchar': types.VARCHAR(length='50'),
            'test_bigint': types.BIGINT,
            'test_datetime': types.DateTime(),
            'test_date': types.DATE(),
            'test_tinyint': types.SMALLINT,
            'test_decimal': types.DECIMAL(precision='20', scale='2'),
            'test_json': types.JSON,
            'test_text': types.TEXT
            }))

        # self.assertEqual(self.oracle.column(self.table),['test_varchar2', 'test_nvachar2', 'test_char', 'test_date', 'test_tinyint', 'test_number', 'test_number2'])

    def test_create(self):
        self.assertEqual(self.mysql.create(self.table),'CREATE TABLE `test_sqlclient` (\n  `test_int` int(11) DEFAULT NULL,\n  `test_varchar` varchar(50) DEFAULT NULL,\n  `test_bigint` bigint(20) DEFAULT NULL,\n  `test_datetime` datetime DEFAULT NULL,\n  `test_date` date DEFAULT NULL,\n  `test_tinyint` tinyint(1) DEFAULT NULL,\n  `test_decimal` decimal(20,2) DEFAULT NULL,\n  `test_json` json DEFAULT NULL,\n  `test_text` text\n) ENGINE=InnoDB DEFAULT CHARSET=utf8')
        self.assertEqual(self.mysql.create(self.table,column='test_int,test_varchar,test_bigint,test_datetime'),'create table tablename (`test_int` int(11) DEFAULT NULL\n,`test_varchar` varchar(50) DEFAULT NULL\n,`test_bigint` bigint(20) DEFAULT NULL\n,`test_datetime` datetime DEFAULT NULL)')

    def test_select(self):
        self.assertEqual(self.mysql.select(self.table),'select\ttest_int\n\t,test_varchar\n\t,test_bigint\n\t,test_datetime\n\t,test_date\n\t,test_tinyint\n\t,test_decimal\n\t,test_json\n\t,test_text\nfrom test_SQLClient')

    def test_insert(self):
        self.assertEqual(self.mysql.insert('test_SQLClient'),'insert into test_SQLClient (\n\ttest_int\n\t,test_varchar\n\t,test_bigint\n\t,test_datetime\n\t,test_date\n\t,test_tinyint\n\t,test_decimal\n\t,test_json\n\t,test_text\n)\n        ')

    def test_values(self):
        G=self.mysql.values(self.table)
        self.assertEqual(G.__next__(),'(\n\t123,\n\t\'123\',\n\t123456,\n\t\'2020-09-02 07:36:27\',\n\t\'2020-09-02\',\n\t1,\n\t\'20.24\',\n\t\'{"a": "b"}\',\n\t\'aabbcc\')')

    def test_procedure(self):
        self.assertEqual(self.mysql.procedure('test_SQLClient'),'CREATE DEFINER=`pgadmin`@`%` PROCEDURE `test_SQLClient`()\nBEGIN\r\n\tSELECT 1;\r\n\r\nEND')
if __name__=='__main__':
    unittest.main(verbosity=2)