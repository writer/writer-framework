import argparse
import asyncio
import os
import shutil
import stat
import tempfile
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from threading import Timer
from typing import Any, Dict, List, Optional, Set, Union

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver


class OperationQueues:
    def __init__(self) -> None:
        self.files_to_update: Dict[str, str] = {}  # Maps dest paths to their source paths
        self.files_to_delete: Set[str] = set()
        self.dirs_to_create: Set[str] = set()
        self.dirs_to_delete: Set[str] = set()
        self.lock = threading.Lock()

    def has_pending_operations(self) -> bool:
        with self.lock:
            return (
                len(self.files_to_update) > 0 or
                len(self.files_to_delete) > 0 or
                len(self.dirs_to_create) > 0 or
                len(self.dirs_to_delete) > 0
            )

    def clear_all(self) -> None:
        with self.lock:
            self.files_to_update.clear()
            self.files_to_delete.clear()
            self.dirs_to_create.clear()
            self.dirs_to_delete.clear()


class FolderSyncHandler(FileSystemEventHandler):
    def __init__(self, src_dir: str, dest_dir: str, verbose: bool, operation_queues: OperationQueues) -> None:
        self.src_dir = Path(src_dir).resolve()
        self.dest_dir = Path(dest_dir).resolve()
        self.verbose = verbose
        self.operation_queues = operation_queues

    def log(self, *args) -> None:
        if self.verbose:
            print(*args)

    def rel(self, path: str) -> str:
        return str(Path(path).relative_to(self.src_dir))

    def dest_path(self, src_path: str) -> str:
        rel_path = self.rel(src_path)
        return str(self.dest_dir / rel_path)

    def on_created(self, event) -> None:
        if event.is_directory:
            with self.operation_queues.lock:
                self.operation_queues.dirs_to_create.add(event.src_path)
            self.log("Queued dir add:", self.rel(event.src_path))
        else:
            dest = self.dest_path(event.src_path)
            with self.operation_queues.lock:
                self.operation_queues.files_to_update[dest] = event.src_path
            self.log("Queued add:", self.rel(event.src_path))

    def on_modified(self, event) -> None:
        if not event.is_directory:
            dest = self.dest_path(event.src_path)
            with self.operation_queues.lock:
                self.operation_queues.files_to_update[dest] = event.src_path
            self.log("Queued change:", self.rel(event.src_path))

    def on_deleted(self, event) -> None:
        if event.is_directory:
            with self.operation_queues.lock:
                self.operation_queues.dirs_to_delete.add(event.src_path)
            self.log("Queued dir remove:", self.rel(event.src_path))
        else:
            dest = self.dest_path(event.src_path)
            with self.operation_queues.lock:
                self.operation_queues.files_to_delete.add(event.src_path)
                # Remove from update queue if present
                self.operation_queues.files_to_update.pop(dest, None)
            self.log("Queued remove:", self.rel(event.src_path))

    def on_moved(self, event) -> None:
        # Handle moves as delete + create
        self.on_deleted(type('MockEvent', (), {'src_path': event.src_path, 'is_directory': event.is_directory})())
        self.on_created(type('MockEvent', (), {'src_path': event.dest_path, 'is_directory': event.is_directory})())


class FileBuffering:
    def __init__(self, dest_dir: str, *, src_dir: Optional[str] = None, verbose: bool = False, interval: int = 10) -> None:
        self.path = src_dir if src_dir is not None else tempfile.mkdtemp()
        self.src_dir = Path(self.path).resolve()
        self.dest_dir = Path(dest_dir).resolve()
        self.verbose = verbose
        self.sync_interval = interval
        self.operation_queues = OperationQueues()
        self.is_sync_in_progress = False
        self.observer: Optional[BaseObserver] = None
        self.sync_timer: Optional[Timer] = None
        self.running = False
        self.last_comparison_time: datetime = datetime.now()
        self.check_interval = 10
        self.check_timer: Optional[Timer] = None

    def log(self, *args) -> None:
        if self.verbose:
            print(*args)

    def rel(self, path: str) -> str:
        return str(Path(path).relative_to(self.src_dir))

    def dest_path(self, src_path: str) -> str:
        rel_path = self.rel(src_path)
        return str(self.dest_dir / rel_path)

    def should_copy(self, src: str, dest: str) -> bool:
        try:
            src_path = Path(src)
            dest_path = Path(dest)
            
            if not dest_path.exists():
                return True
                
            src_stat = src_path.stat()
            dest_stat = dest_path.stat()
            
            # Compare size
            if src_stat.st_size != dest_stat.st_size:
                return True
            
            # Compare modification time (with 1 second tolerance)
            if src_stat.st_mtime > dest_stat.st_mtime + 1:
                return True
            
            # Compare content
            try:
                with open(src, 'rb') as f1, open(dest, 'rb') as f2:
                    return f1.read() != f2.read()
            except Exception:
                return True
                
        except Exception:
            return True

    def ensure_dir(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)

    def copy_file(self, src: str, dest: str) -> None:
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    def remove_path(self, path: str) -> None:
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()

    def init(self) -> None:
        """Initialize by copying all files from destination to source directory."""
        self.log(f"Initializing: copying files from {self.dest_dir} to {self.src_dir}")
        
        # Check if destination directory exists
        if not self.dest_dir.exists():
            self.log(f"Destination directory {self.dest_dir} doesn't exist yet. Nothing to copy.")
            return
        
        def copy_recursively(relative_path: str = ""):
            full_dest = self.dest_dir / relative_path
            full_src = self.src_dir / relative_path
            
            # Ensure the directory exists in source
            self.ensure_dir(str(full_src))
            
            try:
                for entry in full_dest.iterdir():
                    rel_path = str(Path(relative_path) / entry.name) if relative_path else entry.name
                    dest_path = self.dest_dir / rel_path
                    src_path = self.src_dir / rel_path
                    
                    if entry.is_dir():
                        copy_recursively(rel_path)
                    elif entry.is_file():
                        self.copy_file(str(dest_path), str(src_path))
                        self.log(f"Copied to source: {rel_path}")
            except PermissionError as e:
                print(f"Permission error accessing {full_dest}: {e}")
            except Exception as e:
                print(f"Error processing {full_dest}: {e}")
        
        # Execute the recursive copy
        copy_recursively()
        self.log("Initialization complete. All files copied to temporary directory.")
        
    def initial_sync(self) -> None:
        self.log("Starting initial sync...")
        
        def sync_recursively(relative: str = ""):
            full_src = self.src_dir / relative
            full_dest = self.dest_dir / relative
            
            self.ensure_dir(str(full_dest))
            
            try:
                for entry in full_src.iterdir():
                    rel_path = str(Path(relative) / entry.name) if relative else entry.name
                    src_path = self.src_dir / rel_path
                    dst_path = self.dest_dir / rel_path
                    
                    if entry.is_dir():
                        sync_recursively(rel_path)
                    elif entry.is_file():
                        if self.should_copy(str(src_path), str(dst_path)):
                            self.copy_file(str(src_path), str(dst_path))
                            self.log("Copied:", rel_path)
                        else:
                            self.log("Skipped (up to date):", rel_path)
            except PermissionError as e:
                print(f"Permission error accessing {full_src}: {e}")
            except Exception as e:
                print(f"Error processing {full_src}: {e}")
        
        # Run synchronously since it's the initial sync
        sync_recursively()

    def process_batched_operations(self) -> None:
        if self.is_sync_in_progress:
            return
        if not self.operation_queues.has_pending_operations():
            return
        
        self.is_sync_in_progress = True
        self.log(f"Processing batched operations at {datetime.now().isoformat()}")
        
        try:
            with self.operation_queues.lock:
                # Process directory creations first
                if self.operation_queues.dirs_to_create:
                    self.log(f"Creating {len(self.operation_queues.dirs_to_create)} directories")
                    for dir_path in self.operation_queues.dirs_to_create.copy():
                        try:
                            self.log("Dir add:", self.rel(dir_path))
                            to = self.dest_path(dir_path)
                            self.ensure_dir(to)
                        except Exception as e:
                            print(f"Error creating directory {dir_path}: {e}")
                    self.operation_queues.dirs_to_create.clear()
                
                # Process file updates
                if self.operation_queues.files_to_update:
                    self.log(f"Updating {len(self.operation_queues.files_to_update)} files")
                    for dest_path, src_path in self.operation_queues.files_to_update.copy().items():
                        try:
                            if self.should_copy(src_path, dest_path):
                                self.log("File update:", self.rel(src_path))
                                self.copy_file(src_path, dest_path)
                        except Exception as e:
                            print(f"Error updating file {src_path} to {dest_path}: {e}")
                    self.operation_queues.files_to_update.clear()
                
                # Process file deletions
                if self.operation_queues.files_to_delete:
                    self.log(f"Deleting {len(self.operation_queues.files_to_delete)} files")
                    for file_path in self.operation_queues.files_to_delete.copy():
                        try:
                            self.log("File remove:", self.rel(file_path))
                            to = self.dest_path(file_path)
                            self.remove_path(to)
                        except Exception as e:
                            print(f"Error deleting file {file_path}: {e}")
                    self.operation_queues.files_to_delete.clear()
                
                # Process directory deletions last
                if self.operation_queues.dirs_to_delete:
                    self.log(f"Deleting {len(self.operation_queues.dirs_to_delete)} directories")
                    for dir_path in self.operation_queues.dirs_to_delete.copy():
                        try:
                            self.log("Dir remove:", self.rel(dir_path))
                            to = self.dest_path(dir_path)
                            self.remove_path(to)
                        except Exception as e:
                            print(f"Error deleting directory {dir_path}: {e}")
                    self.operation_queues.dirs_to_delete.clear()
                    
        except Exception as error:
            print(f"Error processing batch: {error}")
        finally:
            self.is_sync_in_progress = False
        
        # Compare directories after processing
        self.compare_directories(str(self.src_dir), str(self.dest_dir), self.verbose)

    def schedule_batch_processing(self) -> None:
        if not self.running:
            return
            
        self.process_batched_operations()

        
        # Schedule next processing
        self.sync_timer = threading.Timer(self.sync_interval, self.schedule_batch_processing)
        if self.sync_timer:  # This check is redundant but satisfies mypy
            self.sync_timer.start()

    def schedule_sanity_check(self) -> None:

        if self.last_comparison_time < datetime.now() - timedelta(seconds=5):
            self.compare_directories(str(self.src_dir), str(self.dest_dir), self.verbose)

        self.check_timer = threading.Timer(self.check_interval, self.schedule_sanity_check)
        if self.check_timer:  # This check is redundant but satisfies mypy
            self.check_timer.start()



    def get_all_files(self, directory: str, base_dir: str) -> Dict[str, str]:
        files = {}
        dir_path = Path(directory)
        base_path = Path(base_dir)
        
        def traverse_dir(current_path: Path):
            try:
                for entry in current_path.iterdir():
                    if entry.is_dir():
                        traverse_dir(entry)
                    elif entry.is_file():
                        relative_path = str(entry.relative_to(base_path))
                        files[relative_path] = str(entry)
            except PermissionError:
                pass
        
        traverse_dir(dir_path)
        return files

    def files_have_same_content(self, file1: str, file2: str) -> bool:
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                return f1.read() == f2.read()
        except Exception as e:
            if self.verbose:
                print(f"Error comparing files {file1} and {file2}: {e}")
            return False

    def compare_directories(self, dir1: str, dir2: str, verbose: bool = False) -> List[Dict[str, str]]:
        divergent_files: List[Dict[str, str]] = []
        self.last_comparison_time = datetime.now()
        
        def log_verbose(*args):
            if verbose:
                print(*args)
        
        # Get all files from both directories
        dir1_files = self.get_all_files(dir1, dir1)
        dir2_files = self.get_all_files(dir2, dir2)
        
        # Compare files that exist in both directories
        for relative_path, full_path1 in dir1_files.items():
            full_path2 = dir2_files.get(relative_path)
            
            if not full_path2:
                # File exists in dir1 but not in dir2
                divergent_files.append({'path': relative_path, 'reason': 'missing in target'})
                dest = self.dest_path(full_path1)
                with self.operation_queues.lock:
                    self.operation_queues.files_to_update[dest] = full_path1
                log_verbose(f"File only in source: {relative_path}")
            else:
                # File exists in both, compare content
                if not self.files_have_same_content(full_path1, full_path2):
                    divergent_files.append({'path': relative_path, 'reason': 'content differs'})
                    dest = self.dest_path(full_path1)
                    with self.operation_queues.lock:
                        self.operation_queues.files_to_update[dest] = full_path1
                    log_verbose(f"Content differs: {relative_path}")
        
        # Check for files in dir2 that don't exist in dir1
        for relative_path in dir2_files.keys():
            if relative_path not in dir1_files:
                divergent_files.append({'path': relative_path, 'reason': 'missing in source'})
                with self.operation_queues.lock:
                    self.operation_queues.files_to_delete.add(str(self.src_dir / relative_path))
                log_verbose(f"File only in target: {relative_path}")
        
        return divergent_files

    def watch_changes(self) -> None:
        """
        Set up file system monitoring and start the periodic sync process.
        This method returns immediately after setting up the background watchers.
        """
        handler = FolderSyncHandler(str(self.src_dir), str(self.dest_dir), self.verbose, self.operation_queues)
        self.observer = Observer()
        if self.observer:  # This check is redundant but satisfies mypy
            self.observer.schedule(handler, str(self.src_dir), recursive=True)
            self.observer.start()
        
        print(f"Watching for changes in {self.src_dir}...")
        print(f"Files will be synchronized every {self.sync_interval} seconds")
        
        # Start the batch processing scheduler
        self.running = True
        self.schedule_batch_processing()
        self.schedule_sanity_check()

    def stop(self) -> None:
        self.running = False
        if self.sync_timer:
            self.sync_timer.cancel()
            self.sync_timer.join()
            self.sync_timer = None
        if self.check_timer:
            self.check_timer.cancel()
            self.check_timer.join()
            self.check_timer = None
        if self.observer:
            self.observer.stop()
            self.observer.join()

