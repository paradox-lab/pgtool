import unittest
from unittest import mock
from pgtool.ProgramTool import wxsync


class FunctionTest(unittest.TestCase):
    def test_access_token(self):
        self.assertIsNotNone(wxsync.access_token())


    @mock.patch('requests.post')
    def test_init(self,mock_post):
        data={
            "errcode": 0,
            "errmsg": "ok",
            "job_id": 100074947
            }
        mock_post().text=data

        access_token=wxsync.access_token()
        self.assertEqual(wxsync.init(access_token),data)

    @mock.patch('requests.post')
    def test_delete(self,mock_post):
        data={
            "errcode": 0,
            "errmsg": "ok",
            "deleted": 2
            }
        mock_post().text = data
        access_token = wxsync.access_token()
        self.assertEqual(wxsync.delete(access_token), data)

if __name__ == '__main__':
    unittest.main(verbosity=1)

