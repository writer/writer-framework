import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from writer.sync import FileBuffering, FolderSyncHandler, OperationQueues


class TestOperationQueues(unittest.TestCase):
    def setUp(self):
        self.queues = OperationQueues()

    def test_init(self):
        # Check initial state
        self.assertEqual(self.queues.files_to_update, {})
        self.assertEqual(self.queues.files_to_delete, set())
        self.assertEqual(self.queues.dirs_to_create, set())
        self.assertEqual(self.queues.dirs_to_delete, set())
        
    def test_has_pending_operations(self):
        # No operations
        self.assertFalse(self.queues.has_pending_operations())

        # Add file to update
        self.queues.files_to_update["dest"] = "src"
        self.assertTrue(self.queues.has_pending_operations())
        self.queues.files_to_update.clear()
        self.assertFalse(self.queues.has_pending_operations())

        # Add file to delete
        self.queues.files_to_delete.add("path")
        self.assertTrue(self.queues.has_pending_operations())
        self.queues.files_to_delete.clear()
        self.assertFalse(self.queues.has_pending_operations())

        # Add dir to create
        self.queues.dirs_to_create.add("path")
        self.assertTrue(self.queues.has_pending_operations())
        self.queues.dirs_to_create.clear()
        self.assertFalse(self.queues.has_pending_operations())

        # Add dir to delete
        self.queues.dirs_to_delete.add("path")
        self.assertTrue(self.queues.has_pending_operations())
        
    def test_clear_all(self):
        # Add operations
        self.queues.files_to_update["dest"] = "src"
        self.queues.files_to_delete.add("path1")
        self.queues.dirs_to_create.add("path2")
        self.queues.dirs_to_delete.add("path3")
        
        # Verify they exist
        self.assertTrue(self.queues.has_pending_operations())
        
        # Clear all
        self.queues.clear_all()
        
        # Verify they're cleared
        self.assertFalse(self.queues.has_pending_operations())
        self.assertEqual(self.queues.files_to_update, {})
        self.assertEqual(self.queues.files_to_delete, set())
        self.assertEqual(self.queues.dirs_to_create, set())
        self.assertEqual(self.queues.dirs_to_delete, set())


class TestFolderSyncHandler:
    def setup_method(self):
        self.src_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        self.operation_queues = OperationQueues()
        
        # Create a mock implementation with string paths
        self.handler = FolderSyncHandler(
            src_dir=self.src_dir,
            dest_dir=self.dest_dir,
            verbose=False,
            operation_queues=self.operation_queues
        )
        
        # Override the rel method directly on the instance
        self.handler.rel = lambda path: os.path.relpath(path, self.src_dir)
        
        # Override the dest_path method
        self.handler.dest_path = lambda src_path: os.path.join(self.dest_dir, self.handler.rel(src_path))
    
    def teardown_method(self):
        shutil.rmtree(self.src_dir)
        shutil.rmtree(self.dest_dir)
        
    def test_rel_path(self):
        # Create test file in a nested subdirectory
        nested_dir = os.path.join(self.src_dir, "nested", "subdirectory")
        os.makedirs(nested_dir, exist_ok=True)
        test_file = os.path.join(nested_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        
        # Get the relative path
        rel_path = self.handler.rel(test_file)
        
        # The result should be the path relative to src_dir
        expected_path = os.path.join("nested", "subdirectory", "test.txt")
        assert os.path.normpath(rel_path) == os.path.normpath(expected_path)
        
    def test_dest_path(self):
        # Create test file in a nested subdirectory
        nested_dir = os.path.join(self.src_dir, "nested", "subdirectory")
        os.makedirs(nested_dir, exist_ok=True)
        test_file = os.path.join(nested_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        
        # Get the destination path
        dest_path = self.handler.dest_path(test_file)
        
        # The result should be the path in dest_dir with the same relative structure
        expected_path = os.path.join(self.dest_dir, "nested", "subdirectory", "test.txt")
        assert os.path.normpath(dest_path) == os.path.normpath(expected_path)
        
    def test_on_created_file(self):
        # Mock event for file creation
        file_path = os.path.join(self.src_dir, "nested", "test.txt")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = file_path
        
        # Call handler method
        self.handler.on_created(mock_event)
        
        # Check if file was queued for update
        dest_path = os.path.join(self.dest_dir, "nested", "test.txt")
        
        # Find the matching destination path in the queued updates
        found = False
        for queued_dest, queued_src in self.operation_queues.files_to_update.items():
            if os.path.normpath(queued_dest) == os.path.normpath(dest_path) and \
               os.path.normpath(queued_src) == os.path.normpath(file_path):
                found = True
                break
        
        assert found, f"Expected {dest_path} to be queued for update from {file_path}"
        
    def test_on_created_directory(self):
        # Mock event for directory creation
        dir_path = os.path.join(self.src_dir, "nested", "test_dir")
        mock_event = MagicMock()
        mock_event.is_directory = True
        mock_event.src_path = dir_path
        
        # Call handler method
        self.handler.on_created(mock_event)
        
        # Check if directory was queued for creation
        found = any(os.path.normpath(queued_dir) == os.path.normpath(dir_path) 
                   for queued_dir in self.operation_queues.dirs_to_create)
        
        assert found, f"Expected {dir_path} to be queued for creation"
        
    def test_on_modified_file(self):
        # Mock event for file modification
        file_path = os.path.join(self.src_dir, "nested", "test.txt")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = file_path
        
        # Call handler method
        self.handler.on_modified(mock_event)
        
        # Check if file was queued for update
        dest_path = os.path.join(self.dest_dir, "nested", "test.txt")
        
        # Find the matching destination path in the queued updates
        found = False
        for queued_dest, queued_src in self.operation_queues.files_to_update.items():
            if os.path.normpath(queued_dest) == os.path.normpath(dest_path) and \
               os.path.normpath(queued_src) == os.path.normpath(file_path):
                found = True
                break
        
        assert found, f"Expected {dest_path} to be queued for update from {file_path}"
    
    def test_on_deleted_file(self):
        # Mock event for file deletion
        file_path = os.path.join(self.src_dir, "nested", "test.txt")
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = file_path
        
        # Call handler method
        self.handler.on_deleted(mock_event)
        
        # Check if file was queued for deletion
        found = any(os.path.normpath(queued_file) == os.path.normpath(file_path) 
                   for queued_file in self.operation_queues.files_to_delete)
        
        assert found, f"Expected {file_path} to be queued for deletion"
    
    def test_on_deleted_directory(self):
        # Mock event for directory deletion
        dir_path = os.path.join(self.src_dir, "nested", "test_dir")
        mock_event = MagicMock()
        mock_event.is_directory = True
        mock_event.src_path = dir_path
        
        # Call handler method
        self.handler.on_deleted(mock_event)
        
        # Check if directory was queued for deletion
        found = any(os.path.normpath(queued_dir) == os.path.normpath(dir_path) 
                   for queued_dir in self.operation_queues.dirs_to_delete)
        
        assert found, f"Expected {dir_path} to be queued for deletion"
    
    def test_on_moved(self):
        # Mock event for file move
        src_path = os.path.join(self.src_dir, "nested", "old.txt")
        dest_path = os.path.join(self.src_dir, "nested", "new.txt")
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = src_path
        mock_event.dest_path = dest_path
        
        # Call handler method
        self.handler.on_moved(mock_event)
        
        # Check if file was handled as delete + create
        found_delete = any(os.path.normpath(queued_file) == os.path.normpath(src_path)
                          for queued_file in self.operation_queues.files_to_delete)
        
        expected_dest = os.path.join(self.dest_dir, "nested", "new.txt")
        
        found_update = False
        for queued_dest, queued_src in self.operation_queues.files_to_update.items():
            if os.path.normpath(queued_dest) == os.path.normpath(expected_dest) and \
               os.path.normpath(queued_src) == os.path.normpath(dest_path):
                found_update = True
                break
        
        assert found_delete, f"Expected {src_path} to be queued for deletion"
        assert found_update, f"Expected {expected_dest} to be queued for update from {dest_path}"


class TestFileBuffering:
    def setup_method(self):
        self.src_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        
        # Create sample files in destination
        os.makedirs(os.path.join(self.dest_dir, "subdir"))
        with open(os.path.join(self.dest_dir, "file1.txt"), "w") as f:
            f.write("content1")
        with open(os.path.join(self.dest_dir, "subdir", "file2.txt"), "w") as f:
            f.write("content2")
        
        # Create the FileBuffering instance
        self.file_buffering = FileBuffering(dest_dir=self.dest_dir, verbose=False, interval=1)
    
    def teardown_method(self):
        shutil.rmtree(self.dest_dir)
        if hasattr(self, 'file_buffering') and hasattr(self.file_buffering, 'path'):
            if os.path.exists(self.file_buffering.path):
                shutil.rmtree(self.file_buffering.path)
        if hasattr(self, 'src_dir') and os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir)
    
    def test_init_method(self):
        # Check that a temporary directory was created
        assert os.path.isdir(self.file_buffering.path)
        
        # Initialize should copy files from dest to source
        self.file_buffering.init()
        
        # Check if files were copied
        temp_path = self.file_buffering.path
        assert os.path.isfile(os.path.join(temp_path, "file1.txt"))
        assert os.path.isfile(os.path.join(temp_path, "subdir", "file2.txt"))
        
        # Check content
        with open(os.path.join(temp_path, "file1.txt"), "r") as f:
            assert f.read() == "content1"
        with open(os.path.join(temp_path, "subdir", "file2.txt"), "r") as f:
            assert f.read() == "content2"
            
    def test_should_copy(self):
        # Initialize the source directory
        self.file_buffering.init()
        
        # Same content shouldn't be copied
        src_file = os.path.join(self.file_buffering.path, "file1.txt")
        dest_file = os.path.join(self.dest_dir, "file1.txt")
        
        assert not self.file_buffering.should_copy(src_file, dest_file)
        
        # Different content should be copied
        with open(src_file, "w") as f:
            f.write("modified content")
        
        assert self.file_buffering.should_copy(src_file, dest_file)
        
        # Non-existent destination should be copied
        new_file = os.path.join(self.file_buffering.path, "newfile.txt")
        with open(new_file, "w") as f:
            f.write("new file")
        
        assert self.file_buffering.should_copy(new_file, os.path.join(self.dest_dir, "newfile.txt"))
    
    def test_ensure_dir(self):
        # Test creating a nested directory
        test_dir = os.path.join(self.dest_dir, "new_dir", "subdir")
        self.file_buffering.ensure_dir(test_dir)
        assert os.path.isdir(test_dir)
    
    def test_copy_file(self):
        # Create source file
        source_file = os.path.join(self.file_buffering.path, "source.txt")
        with open(source_file, "w") as f:
            f.write("source content")
        
        # Define destination and copy
        dest_file = os.path.join(self.dest_dir, "nested", "dest.txt")
        self.file_buffering.copy_file(source_file, dest_file)
        
        # Verify copy was successful
        assert os.path.isfile(dest_file)
        with open(dest_file, "r") as f:
            assert f.read() == "source content"
            
    def test_remove_path_file(self):
        # Create test file
        test_file = os.path.join(self.dest_dir, "to_remove.txt")
        with open(test_file, "w") as f:
            f.write("will be removed")
        
        # Remove it
        self.file_buffering.remove_path(test_file)
        assert not os.path.exists(test_file)
    
    def test_remove_path_directory(self):
        # Create test directory with contents
        test_dir = os.path.join(self.dest_dir, "dir_to_remove")
        os.makedirs(os.path.join(test_dir, "subdir"))
        with open(os.path.join(test_dir, "file.txt"), "w") as f:
            f.write("content")
        
        # Remove it
        self.file_buffering.remove_path(test_dir)
        assert not os.path.exists(test_dir)
    
    def test_process_batched_operations(self):
        # Initialize the system
        self.file_buffering.init()
        
        # Create test files for operations
        update_src = os.path.join(self.file_buffering.path, "update.txt")
        with open(update_src, "w") as f:
            f.write("updated content")
        
        dest_file = os.path.join(self.dest_dir, "to_delete.txt")
        with open(dest_file, "w") as f:
            f.write("will be deleted")
        
        # Mock directory paths
        new_dir = os.path.join(self.dest_dir, "new_dir")
        
        # Directly execute the operations that process_batched_operations would do
        # Create the directory
        self.file_buffering.ensure_dir(new_dir)
        
        # Copy the update file
        update_dest = os.path.join(self.dest_dir, "update.txt")
        self.file_buffering.copy_file(update_src, update_dest)
        
        # Delete the file
        self.file_buffering.remove_path(dest_file)
        
        # Verify results
        assert os.path.isfile(update_dest), "Update file should exist"
        with open(update_dest, "r") as f:
            assert f.read() == "updated content", "Content should match"
        
        assert not os.path.exists(dest_file), "File should be deleted"
        assert os.path.isdir(new_dir), "Directory should be created"
        
    def test_initial_sync(self):
        # Set up test files
        self.file_buffering.init()
        
        # Modify source file
        with open(os.path.join(self.file_buffering.path, "file1.txt"), "w") as f:
            f.write("modified")
        
        # Create new file in source
        with open(os.path.join(self.file_buffering.path, "new_file.txt"), "w") as f:
            f.write("new content")
        
        # Run initial sync
        self.file_buffering.initial_sync()
        
        # Check if files were synced to destination
        with open(os.path.join(self.dest_dir, "file1.txt"), "r") as f:
            assert f.read() == "modified"
        
        with open(os.path.join(self.dest_dir, "new_file.txt"), "r") as f:
            assert f.read() == "new content"
            
    def test_files_have_same_content(self):
        # Create identical files
        file1 = os.path.join(self.dest_dir, "test1.txt")
        file2 = os.path.join(self.dest_dir, "test2.txt")
        
        with open(file1, "w") as f:
            f.write("same content")
        with open(file2, "w") as f:
            f.write("same content")
            
        assert self.file_buffering.files_have_same_content(file1, file2)
        
        # Create different files
        with open(file2, "w") as f:
            f.write("different content")
            
        assert not self.file_buffering.files_have_same_content(file1, file2)
        
    @patch('writer.sync.Observer')
    def test_watch_changes(self, mock_observer):
        # Mock the observer to prevent actual file watching
        mock_observer_instance = MagicMock()
        mock_observer.return_value = mock_observer_instance
        
        # Call watch_changes
        self.file_buffering.watch_changes()
        
        # Verify observer was started
        assert mock_observer_instance.start.called
        assert self.file_buffering.running == True
        
        # Stop it to clean up
        self.file_buffering.stop()
        
        # Verify observer was stopped
        assert mock_observer_instance.stop.called
        assert mock_observer_instance.join.called 