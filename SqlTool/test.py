import unittest
from sql_client import SQLClient
global S
S = SQLClient('GP_STORE_DEV')
class TestSQLClientMethons(unittest.TestCase):

    def test_select(self):
        self.assertEqual(S.select('banner_rd_mapping'),"""select\tid\n\t,gmt_create\n\t,gmt_modified\n\t,rd_name\n\t,banner_id\n\t,banner_rd_id\n\t,rd_reporting_top_banner\n\t,xxis_code\n\t,gcdb_code_id\n\t,gcdb_code_number\nfrom banner_rd_mapping""")

    def test_table(self):
        self.assertIsNotNone(S.table())

    def test_get_column_from_create(self):
        sql="""	CREATE TEMPORARY TABLE Temp_userinfo (
    app_key varchar(32),
	username varchar(256),
    Email varchar(128),
    enabled tinyint(4),
    id varchar(32),     
	NAME_EN varchar(256),
	NAME_CN varchar(256),
    phone_number varchar(32),  
	case_enable tinyint(4),
	email_enable tinyint(4)
	);"""
        self.assertEqual(S.get_column_from_create(sql),'app_key,\nusername,\nEmail,\nenabled,\nid,\nNAME_EN,\nNAME_CN,\nphone_number,\ncase_enable,\nemail_enable')

if __name__ == '__main__':
    unittest.main()
    S.conn.close()