import unittest
from tkinter import Tk
from pgtool.ProgramTool.program_client import Application

class ApplicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=Application()
    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.parent.destroy()
        del cls.app

    def test_init(self):
        self.assertEqual(self.app.language,['py', 'go', 'java', 'bas', 'js', 'html', 'css', 'wxml', 'wxss', 'sql', 'oracle', 'mysql', 'mssql'])

if __name__=='__main__':
    unittest.main()
