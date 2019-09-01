import os
import random
from filecmp import dircmp

from Jumpscale import j

from .base_test import BaseTest


class FS(BaseTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_dir = None

    def tearDown(self):
        if self.base_dir:
            j.sal.fs.remove(self.base_dir)

    def create_tree(self):
        """Create a tree with many sub directories and files.
        """
        self.parents = {}
        self.base_dir = os.path.join("/tmp", self.random_string())
        for _ in range(3):
            parent_name = self.random_string()
            parent_path = os.path.join(self.base_dir, parent_name)
            j.sal.fs.createDir(parent_path)
            self.parents[parent_path] = []

            types = ["logs", "txts", "pys", "mds", "symlinks"]
            for t in types:
                child_path = os.path.join(parent_path, t)
                j.sal.fs.createDir(child_path)

                files = []
                for _ in range(3):
                    file_name = "{name}.{ext}".format(name=self.random_string(), ext=t[:-1])
                    file_path = os.path.join(child_path, file_name)
                    if t == "symlinks":
                        src = os.path.join(parent_path, "pys")
                        os.symlink(src, file_path, target_is_directory=True)
                        content = os.readlink(file_path)
                    elif t == "mds":
                        content = "{name}: " + self.random_string()
                        j.sal.fs.writeFile(file_path, content)
                    else:
                        content = self.random_string()
                        j.sal.fs.writeFile(file_path, content)
                    files.append({file_path: content})
                self.parents[parent_path].append({child_path: files})
        return self.parents

    # def dirs_equal(self, dir_path_1, dir_path_2):
    #     dcmp = dircmp(dir_path_1, dir_path_2)
    #     if dcmp.diff_files:
    #         return False
    #     for d in dcmp.subdirs.keys():
    #         subdirs = dcmp.left[].subdirs

    def test001_create_exist_move_rename_delete_dir(self):
        """TC340
        Test case for creating, moving, renaming and deleting directory.

        **Test scenario**
        #. Create a directory (D1) under /tmp.
        #. Check that (D1) is created.
        #. Move it to /tmp/(D2).
        #. Check that this directory is moved.
        #. Rename this directory to (D3).
        #. Check that (D3) is exists.
        #. Delete (D3) directory and check that it is not exists.
        """
        self.info("Create a directory (D1) under /tmp.")
        dir_name_1 = self.random_string()
        dir_path_1 = os.path.join("/tmp", dir_name_1)
        j.sal.fs.createDir(dir_path_1)

        self.info("Check that (D1) is created.")
        self.assertTrue(os.path.isdir(dir_path_1))
        self.assertTrue(j.sal.fs.isDir(dir_path_1))
        self.assertTrue(os.path.exists(dir_path_1))
        self.assertTrue(j.sal.fs.exists(dir_path_1))

        self.info("Move it to /tmp/(D2).")
        dir_name_2 = self.random_string()
        dir_path_2 = os.path.join("/tmp", dir_name_2)
        j.sal.fs.moveDir(dir_path_1, dir_path_2)

        self.info("Check that this directory is moved.")
        self.assertTrue(os.path.exists(dir_path_2))
        self.assertFalse(os.path.exists(dir_path_1))

        self.info("Rename this directory to (D3).")
        dir_name_3 = self.random_string()
        dir_path_3 = os.path.join("/tmp", dir_name_3)
        j.sal.fs.renameDir(dir_path_2, dir_path_3)

        self.info("Check that (D3) is exists.")
        self.assertTrue(os.path.exists(dir_path_3))
        self.assertFalse(os.path.exists(dir_path_2))

        self.info("Delete (D3) directory and check that it is not exists.")
        j.sal.fs.remove(dir_path_3)
        self.assertFalse(os.path.exists(dir_path_3))

    def test002_write_append_read_delete_file(self):
        """TC341
        Test case for writing, appending, reading and deleting file.

        **Test scenario**
        #. Write a file under /tmp.
        #. Check that the file is exists and check its content.
        #. Read this file using sal.fs and check that it has same content.
        #. Append content to this file.
        #. Check that file content, the new content should be found.
        #. Write to same file without appending.
        #. Check that the new content is only exists.
        #. Delete this file.
        """
        self.info("Write a file under /tmp.")
        file_name = self.random_string()
        file_content = self.random_string()
        file_path = os.path.join("/tmp", file_name)
        j.sal.fs.writeFile(filename=file_path, contents=file_content, append=False)

        self.info("Check that the file is exists and check its content.")
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(j.sal.fs.exists(file_path))
        self.assertTrue(os.path.isfile(file_path))
        self.assertTrue(j.sal.fs.isFile(file_path))
        with open(file_path, "r") as f:
            content_1 = f.read()
        self.assertEquals(content_1, file_content)

        self.info("Read this file using sal.fs and check that it has same content.")
        content_2 = j.sal.fs.readFile(file_path)
        self.assertEquals(content_2, file_content)

        self.info("Append content to this file.")
        append = self.random_string()
        j.sal.fs.writeFile(filename=file_path, contents=append, append=True)

        self.info("Check that file content, the new content should be found.")
        with open(file_path, "r") as f:
            new_content_1 = f.read()
        self.assertEquals(new_content_1, file_content + append)

        self.info("Write to same file without appending.")
        j.sal.fs.writeFile(filename=file_path, contents=append, append=False)

        self.info("Check that the new content is only exists.")
        with open(file_path, "r") as f:
            new_content_2 = f.read()
        self.assertEquals(new_content_2, append)

        self.info("Delete this file.")
        j.sal.fs.remove(file_path)
        self.assertFalse(os.path.exists(file_path))

    def test003_create_move_rename_copy_file(self):
        """TC342
        Test case for creating, moving, renaming and copying files.

        **Test scenario**
        #. Create an empty file.
        #. Check that the file is exists.
        #. Create a directory and move this file to this directory.
        #. Check that the file is moved.
        #. Rename this file and Check that the file is renamed.
        #. Copy this file to a non-existing directory, should fail.
        #. Copy this file to a non-existing directory with createDirIfNeeded=True, should success.
        #. Check that file is copied.
        #. Write a word to the copied file.
        #. Try to copy this file again to the same directory with overwriteFile=False.
        #. Check the content of the copied file, should not be changed.
        #. Try again to copy this file to the same directory with overwriteFile=True.
        #. Check the content of the copied file, should be changed.
        """
        self.info("Create an empty file.")
        file_name_1 = self.random_string()
        file_path_1 = os.path.join("/tmp", file_name_1)
        j.sal.fs.createEmptyFile(file_path_1)

        self.info("Check that the file is exists.")
        self.assertTrue(os.path.exists(file_path_1))

        self.info("Create a directory and move this file to this directory.")
        dir_name_1 = self.random_string()
        dir_path_1 = os.path.join("/tmp", dir_name_1)
        j.sal.fs.createDir(dir_path_1)
        j.sal.fs.moveFile(file_path_1, dir_path_1)

        self.info("Check that the file is moved.")
        file_path_2 = os.path.join(dir_path_1, file_name_1)
        self.assertTrue(os.path.exists(file_path_2))
        self.assertFalse(os.path.exists(file_path_1))

        self.info("Rename this file and Check that the file is renamed.")
        file_name_2 = self.random_string()
        file_path_3 = os.path.join(dir_path_1, file_name_2)
        j.sal.fs.renameFile(file_path_2, file_path_3)
        self.assertTrue(os.path.exists(file_path_3))
        self.assertFalse(os.path.exists(file_path_2))

        self.info("Copy this file to a non-existing directory, should fail.")
        dir_name_2 = self.random_string()
        dir_path_2 = os.path.join("/tmp", dir_name_2)
        file_path_4 = os.path.join(dir_path_2, file_name_2)
        with self.assertRaises(Exception):
            j.sal.fs.copyFile(file_path_3, file_path_4, createDirIfNeeded=False)

        self.info("Copy this file to a non-existing directory with createDirIfNeeded=True, should success.")
        j.sal.fs.copyFile(file_path_3, file_path_4, createDirIfNeeded=True)

        self.info("Check that file is copied.")
        self.assertTrue(os.path.exists(file_path_4))
        self.assertTrue(os.path.exists(file_path_3))

        self.info("Write a word (W) to the copied file.")
        file_content = self.random_string()
        j.sal.fs.writeFile(file_path_3, file_content)

        self.info("Try to copy this file again to the same directory with overwriteFile=False.")
        j.sal.fs.copyFile(file_path_4, file_path_3, overwriteFile=False)

        self.info("Check the content of the copied file, should not be changed.")
        content_1 = j.sal.fs.readFile(file_path_3)
        self.assertEquals(content_1, file_content)

        self.info("Try again to copy this file to the same directory with overwriteFile=True.")
        j.sal.fs.copyFile(file_path_4, file_path_3, overwriteFile=True)

        self.info("Check the content of the copied file, should be changed.")
        content_1 = j.sal.fs.readFile(file_path_3)
        self.assertNotEquals(content_1, file_content)

        self.info("Delete all files has been created")
        j.sal.fs.remove(dir_path_1)
        j.sal.fs.remove(dir_path_2)

    def test004_copytree(self):
        """TC343
        Test case for copying tree using j.sal.fs.copyDirTree.

        **Test scenario**
        #. Create a tree with many sub directories, files and symlinks.
        #. Copy this tree with keepsymlinks=False.
        #. Compare copied tree with the original one, should not be the same.
        #. Copy this tree with keepsymlinks=True.
        #. Compare copied tree with original one, should be the same.
        #. Check that the copied tree files has symlinks.
        #. Copy this tree with deletefirst=True and destination must be the last copied tree.
        #. Compare the copied tree with original one, should be the same.
        #. Change the content of some files in the destination directory.
        #. Copy the tree to the same destination directory with overwriteFiles=False.
        #. Check the changed files, should be the same.
        #. Copy the tree to the same destination directory with overwriteFiles=True.
        #. Check the changed files, should be changed to the original.
        #. Copy the tree with ignoring sub directory.
        #. Check that this directory is not copied.
        #. Copy this tree with ignoring list of files.
        #. Check that these files are not in copied tree.
        #. Copy this tree with recursive=False.
        #. Check that files and directories of sub directories are not exists.
        #. Copy this tree to directory contains different files with rsyncdelete=False.
        #. Check that the destination has its original files.
        #. Copy this tree to directory contains different files with rsyncdelete=True.
        #. Check that the destination has not its original files.
        """
        pass
        # self.info("Create a tree with many sub directories, files and symlinks.")
        # tree = self.create_tree()

        # self.info("Copy this tree with keepsymlinks=False.")
        # dir_name = self.random_string()
        # dir_path = os.path.join("/tmp", dir_name)
        # j.sal.fs.copyDirTree(self.base_dir, dir_path, keepsymlinks=False)
        # import ipdb

        # ipdb.set_trace()
        # self.info("Compare copied tree with the original one, should not be the same.")
        # self.assertFalse(j.sal.fs.dirEqual(self.base_dir, dir_path))
        # j.sal.fs.remove(dir_path)

        # self.info("Copy this tree with keepsymlinks=True.")
        # dir_name = self.random_string()
        # dir_path = os.path.join("/tmp", dir_name)
        # j.sal.fs.copyDirTree(self.base_dir, dir_path, keepsymlinks=True)

        # self.info("Compare copied tree with original one, should be the same.")
        # self.assertTrue(j.sal.fs.dirEqual(self.base_dir, dir_path))
        # j.sal.fs.remove(dir_path)

    def test005_list_dirs_in_dir(self):
        """TC344
        Test case for listing directories in a directory using j.sal.fs.listDirsInDir.

        **Test scenario**
        #. Create a tree with many subdirectories.
        #. List the parent directory of this tree with recursive=False, should return the full path of the children only.
        #. List the parent directory of this tree with recursive=True, should return the full path of all subdirectories.
        #. List the parent directory of this tree with dirNameOnly=True, should return only the names of children.
        #. Create another tree and put symlink to it in the first one.
        #. List the original parent with findDirectorySymlinks=True and followSymlinks=True, should return both trees and a symlink.
        #. List the original parent with findDirectorySymlinks=True and followSymlinks=False, should return the original tree with symlink to the second one.
        #. List the original parent with findDirectorySymlinks=False and followSymlinks=True, should return both trees.
        #. List the original parent with findDirectorySymlinks=False and followSymlinks=False, should return the original tree only.
        """
        pass

    def test006_list_files_and_dirs_in_dir(self):
        """TC345
        Test case for listing files and directories in a directory using j.sal.fs.listFilesAndDirsInDir

        **Test scenario**
        #. Create a tree with many sub directories and files.
        #. List the parent directory of this tree with recursive=False, should return the children only.
        #. List the parent directory of this tree with recursive=True, should return all sub directory.
        #. List the parent directory of this tree using filter=*.*, should return all files and directories with dot.
        #. Modify a file and take timestamp of now (T1).
        #. List the parent directory of this tree with minmtime=T1 + 10, should not find the modified file.
        #. List the parent directory of this tree with minmtime=T1 - 10, should file the modified file.
        #. List the parent directory of this tree with maxmtime=T1 + 10, should file the modified file.
        #. List the parent directory of this tree with maxmtime=T1 - 10, should not file the modified file.
        #. List the parent directory of this tree with depth=1, should return only its children.
        #. List the parent directory of this tree with depth=2, should return only its children and grandchildren.
        #. List the parent directory of this tree with type="f", should return only the files.
        #. List the parent directory of this tree with type="d", should return only the directories.
        #. List the original parent with listSymlinks=True and followSymlinks=True, should return both trees and a symlink.
        #. List the original parent with listSymlinks=True and followSymlinks=False, should return the original tree with symlink to the second one.
        #. List the original parent with listSymlinks=False and followSymlinks=True, should return both trees.
        #. List the original parent with listSymlinks=False and followSymlinks=False, should return the original tree only.
        """

    def test007_list_files_in_dir(self):
        """TC346
        Test case for listing files in directory using j.sal.fs.listFilesInDir.

        **Test scenario**
        #. Create a tree with many sub directories and files.
        #. List the parent directory of this tree with recursive=False, should return the children files only.
        #. List the parent directory of this tree with recursive=True, should return all files.
        #. List the parent directory of this tree using filter=*.*, should return all files with dot.
        #. Modify a file and take timestamp of now (T1).
        #. List the parent directory of this tree with minmtime=T1 + 10, should not find the modified file.
        #. List the parent directory of this tree with minmtime=T1 - 10, should file the modified file.
        #. List the parent directory of this tree with maxmtime=T1 + 10, should file the modified file.
        #. List the parent directory of this tree with maxmtime=T1 - 10, should not file the modified file.
        #. List the parent directory of this tree with depth=1, should return only its children files.
        #. List the parent directory of this tree with depth=2, should return only its children and grandchildren files.
        #. Create a file (F1) with upper and lower cases in its name.
        #. List the parent directory of this tree with case_sensitive="insensitive" and exclude=[F1] (F1 should be case insensitive), should return all files except F1.
        #. List the parent directory of this tree with case_sensitive="sensitive" and exclude=[F1] (F1 should be case insensitive), should return all files except F1.
        #. List the parent directory of this tree with case_sensitive="insensitive" and exclude=[F1] (F1 should be case sensitive), should return all files except F1.
        #. List the parent directory of this tree with case_sensitive="sensitive" and exclude=[F1] (F1 should be case sensitive), should return all files.
        #. List the parent directory of this tree with case_sensitive="os" and exclude=[F1] (F1 should be case sensitive), should return all files except F1.
        #. List the parent directory of this tree with case_sensitive="os" and exclude=[F1] (F1 should be case insensitive), should return all files.
        #. List the original parent with listSymlinks=True and followSymlinks=True, should return both trees and a symlink.
        #. List the original parent with listSymlinks=True and followSymlinks=False, should return the original tree with symlink to the second one.
        #. List the original parent with listSymlinks=False and followSymlinks=True, should return both trees.
        #. List the original parent with listSymlinks=False and followSymlinks=False, should return the original tree only.
        """
        pass

    def test_008_list_py_scrpits(self):
        """TC347
        Test case for listing python scripts using j.sal.fs.listPyScriptsInDir.

        **Test scenario**
        #. Create a tree with many sub directories and different files (must contain python files).
        #. List the parent directory of this tree with recursive=False, should return its children python scripts.
        #. List the parent directory of this tree with recursive=True, should return all python scripts under this tree.
        #. Create a python file with special word (W) in its name.
        #. List the parent directory of this tree with (W) as a filter, should return only this script. 
        """
        pass

    def test_009_file_permissions(self):
        """TC348
        Test case for changing files permissions.

        **Test scenario**
        #. Create an empty file.
        #. Change this file's permissions.
        #. Check the this file's permissions, should be changed.
        #. Create a user (U)
        #. Change this file's user to (U).
        #. Check that file's user has been changed.
        #. Change this file's group.
        #. Check that file's group has been changed
        """
        pass

    def test010_file_linking(self):
        """TC349
        Test case for linking and unlinking files.
        
        **Test scenario**
        #. Create a file.
        #. Create a symlink (S) to this file.
        #. Check that (S) is a link with check_valid=True, should be a link
        #. Delete the file.
        #. Check that (S) is a link with check_valid=True, should be a broken link.
        #. Check that (S) is a broken link with remove_if_broken=False, should return False and keep the file.
        #. Check that (S) is a broken link with remove_if_broken=True, should return False and remove the file.
        #. Create a directory (D1).
        #. Create a symlink and use target=D1, should fail.
        #. Create a symlink and use target=D1 with overwrite=True, should success.
        #. Check that the link is created.
        #. Remove the link and check that it is removed.
        #. Create some symlinks under a directory (D2).
        #. Remove the links under D2 and check that they are removed.
        """
        pass

    def test011_link_all_files_and_dirs_in_dir(self):
        """TC350
        Test case for linking all children files and directories in directory.

        **Test scenario**
        #. Create some files with different extension and directories under a directory (D1).
        #. Create symlinks for all files under (D1) and target a directory (D2) with includeDirs=False.
        #. Check that symlinks are created for files only.
        #. Create symlinks for all files under (D1) and target (D2) with includeDirs=True.
        #. Check that symlinks are created for all files and directories.
        #. Remove one of the symlinks and create a file with same name.
        #. Try to Create symlinks for all files and directories under (D1) and target (D2) with delete=False, should fail.
        #. Try again to Create symlinks for all files and directories under (D1) and target (D2) with delete=True, should success.
        #. Create symlinks for all files and directories under (D1) and target (D2) with makeExecutable=True.
        #. Check that the files created are executable.
        #. Remove all symlinks under (D2).
        #. Check that symlinks are removed.
        """
        pass

    def test012_get_information(self):
        """TC351
        Test case for getting information about files and directories.

        **Test scenario**
        #. Create a tree with many sub directories and files.
        #. Get base name of of a directory (full path) and check that the return value eqauls to the directory's name.
        #. Get base name of of a file (full path) with removeExtension=True and check the file's name without extension, should be the same.
        #. Get directory name of a file and check that it is returning parent directory(full path).
        #. Get directory name of a file with lastOnly=True and check that it is returning parent directory only.
        #. Get directory name of a file with levelUp=0 and check that it is returning parent directory only.
        #. Get file extension of a file and check the returning value is the file's extension.
        #. Get parent directory of a file and check this directory parent, should be the same.
        #. Get parent of a directory if it is exists, should return the parent.
        #. Delete this directory and try to get it again with die=True, should raise error.
        #. Delete this directory and try to get it again with die=False, should return None.
        """
        pass

    def test013_get_path_of_running_function(self):
        """TC352
        Test case for getting path of a running function.

        **Test scenario**
        #. Get path of a method in the same file.
        #. Check that the path has been returned, should be the current file path.
        """
        self.info("Get path of a method in the same file.")
        func_path = j.sal.fs.getPathOfRunningFunction(self.create_tree)

        self.info("Check that the path has been returned, should be the current file path.")
        path = __file__
        self.assertEquals(func_path, path)

    def test014_get_tmp_directory_or_file(self):
        """TC353
        Test case for getting a temp directory or file.

        **Test scenario**
        #. Get temporary directory with create=False, should return a random path.
        #. Check that the random path is not exists.
        #. Get temporary directory with create=True, should return a random path.
        #. Check that the random path is exists.
        #. Get temporary directory with random name, should return a path.
        #. Check that this directory is created.
        #. Get random file and check that file is created.
        """
        pass

    def test015_compress(self):
        """TC354
        Test case for compress files.

        **Test scenario**
        #. Create a tree with many sub directories, files and symlinks.
        #. Compress this tree with followlinks=False, should not compress the content of symlinks.
        #. Compress this tree with followlinks=True, should compress the content of symlinks. 
        """
        pass

    def test016_path_parse(self):
        """TC355
        Test case for path parsing.

        **Test scenario**
        #. Get path parsing for a directory, should return (directory path, "", "", 0).
        #. Get path parsing for a file, should return (parent directory, file name, file extension, 0).
        #. Get path parsing for a file with numeric character(N) at the beginning, should return (parent directory, file name, file extension, N).
        #. Get path parsing for a file with baseDir=parent directory, should return ("", file name, file extension, 0).
        #. Get path parsing for non-existing file with existCheck=False, should return (parent directory, file name, file extension, 0).
        #. Get path parsing for non-existing file with existCheck=True, should rasie an error.
        #. Get path parsing for a directory with checkIsFile=False, should return (parent directory, file name, file extension, 0).
        #. Get path parsing for a directory with checkIsFile=True, should raise an error.
        """
        self.info('Get path parsing for a directory, should return (directory path, "", "", 0).')
        dir_path = "/tmp/{}/".format(self.random_string())
        j.sal.fs.createDir(dir_path)
        path_parse = j.sal.fs.pathParse(dir_path)
        excepted_parse = (os.path.normpath(dir_path), "", "", 0)
        self.assertEquals(path_parse, excepted_parse)

        self.info("Get path parsing for a file, should return (parent directory, file name, file extension, 0).")
        file_name = self.random_string()
        extension = "py"
        full_file_name = "{}.{}".format(file_name, extension)
        file_path = os.path.join(dir_path, full_file_name)
        j.sal.fs.createEmptyFile(file_path)
        path_parse = j.sal.fs.pathParse(file_path)
        excepted_parse = (dir_path, file_name, extension, 0)
        self.assertEquals(path_parse, excepted_parse)

        self.info(
            "Get path parsing for a file with numeric character(N) at the beginning, should return (parent directory, file name, file extension, N)."
        )
        num = random.randint(1, 100)
        file_name = self.random_string()
        extension = "txt"
        full_file_name = "{}_{}.{}".format(num, file_name, extension)
        file_path = os.path.join(dir_path, full_file_name)
        j.sal.fs.createEmptyFile(file_path)
        path_parse = j.sal.fs.pathParse(file_path)
        excepted_parse = (dir_path, file_name, extension, str(num))
        self.assertEquals(path_parse, excepted_parse)

        self.info("Delete created files.")
        j.sal.fs.remove(dir_path)

    def test017_change_files_name(self):
        """TC356
        Test case for changing files names using j.sal.fs.changeFileNames.

        **Test scenario**
        #. Create a tree with many sub directories and files with a common word (W1) in their names.
        #. Change these files names by replacing (W1) with another word (W2) with recursive=True.
        #. Check that files names are changed.
        #. Change these files names again by replacing (W2) with another word (W1) with recursive=False.
        #. Check that children files are only changed.
        #. Create a file with (W1) and numeric character(N) at the beginning.
        #. Change these files names by replacing (W1) with another word (W2) with filter=N*.
        #. Check that only this file is changed.
        #. Change the files names depending on modification time.
        """
        pass

    def test018_current_dir(self):
        """TC357
        Test case for getting and changing current working directory.
        **Test scenario**
        #. Get current working directory and check it.
        #. Change working directory and check it.
        """
        self.info("Get current working directory and check it.")
        cur_path = j.sal.fs.getcwd()
        path = os.path.abspath(".")
        self.assertEquals(cur_path, path)

        self.info("Change working directory and check it.")
        path = "/tmp"
        j.sal.fs.changeDir(path)
        cur_path = j.sal.fs.getcwd()
        self.assertEquals(cur_path, path)

    def test019_write_read_check_size_binary_file(self):
        """TC358
        Test case for writting, reading and checking binary file.

        **Test scenario**
        #. Write binary file.
        #. Check that file has been created and it is a binary file.
        #. Read this file and check that its content.
        #. Get file size and check it.
        """
        pass

    def test020_md5sum(self):
        """TC359
        Test case for getting md5sum for a file and directory.

        **Test scenario**
        #. Create a file and get its md5sum.
        #. Calculate this file md5sum.
        #. Check that both md5sum are the same.
        #. Create a directory with some files.
        #. Get the md5sum for this directory using j.sal.fs.getFolderMD5sum.
        #. Calculate the md5sum for this directory.
        #. Check that both md5sum are the same.
        """
        pass

    def test021_replace_word_in_files(self):
        """TC360
        Test case for replacing words in files.
        
        **Test scenario**
        #. Create a tree with many sub directories and files with a {name} (W1) in their contents.
        #. Create template engine and add a replacement to replace name to any random string(S).
        #. Replace words in files under the directory contains these files with recursive=False.
        #. Check that {name} has been replaced to (S) in children files only.
        #. Replace words in files under the directory contains these files with recursive=True.
        #. Check that {name} has been replaced to (S) in all files.
        """
        pass

    def test022_path_operation(self):
        """SAL-021
        Test case for path operations.

        **Test scenario**
        #. 
        """
        pass
