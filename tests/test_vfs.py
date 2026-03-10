import unittest
from deception.filesystem import VirtualFileSystem

class TestVirtualFileSystem(unittest.TestCase):
    def setUp(self):
        self.vfs = VirtualFileSystem()

    def test_initial_state(self):
        self.assertEqual(self.vfs.cwd, "/root")
        self.assertTrue(self.vfs.is_dir("/etc"))
        self.assertTrue(self.vfs.is_file("/etc/passwd"))

    def test_cd(self):
        self.assertTrue(self.vfs.change_dir("/etc"))
        self.assertEqual(self.vfs.cwd, "/etc")
        self.assertFalse(self.vfs.change_dir("/nonexistent"))
        self.assertEqual(self.vfs.cwd, "/etc")
        self.vfs.change_dir("..")
        self.assertEqual(self.vfs.cwd, "/")

    def test_mkdir(self):
        success, msg = self.vfs.mk_dir("/tmp/testdir")
        self.assertTrue(success)
        self.assertTrue(self.vfs.is_dir("/tmp/testdir"))
        
    def test_touch_and_rm(self):
        self.vfs.write_file("/tmp/testfile", "content")
        self.assertTrue(self.vfs.is_file("/tmp/testfile"))
        self.assertEqual(self.vfs.get_file_content("/tmp/testfile"), "content")
        
        self.vfs.remove("/tmp/testfile")
        self.assertFalse(self.vfs.exists("/tmp/testfile"))

if __name__ == '__main__':
    unittest.main()
