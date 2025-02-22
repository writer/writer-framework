import os
import threading
import time

import boto3
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class S3SyncHandler(FileSystemEventHandler):
    """Handles filesystem events and syncs files with S3-compatible storage."""

    def __init__(
        self, local_directory, s3_bucket, s3_prefix="", s3_endpoint=None, sync_interval=10
    ):
        self.local_directory = local_directory
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.s3_client = (
            boto3.client("s3", endpoint_url=s3_endpoint) if s3_endpoint else boto3.client("s3")
        )
        self.sync_interval = sync_interval

        # Storage for pending changes
        self.pending_uploads = set()
        self.pending_deletions = set()
        self.lock = threading.Lock()

        # Start background sync thread
        self.sync_thread = threading.Thread(target=self.sync_to_s3, daemon=True)
        self.sync_thread.start()

    def sync_to_s3(self):
        """Periodically batch sync changes to S3."""
        while True:
            time.sleep(self.sync_interval)
            with self.lock:
                if self.pending_uploads or self.pending_deletions:
                    print(
                        f"Syncing {len(self.pending_uploads)} uploads and {len(self.pending_deletions)} deletions to S3..."
                    )

                    for file_path in self.pending_uploads.copy():
                        self.upload_file_to_s3(file_path)
                    self.pending_uploads.clear()

                    for file_path in self.pending_deletions.copy():
                        self.delete_file_from_s3(file_path)
                    self.pending_deletions.clear()

    def upload_file_to_s3(self, local_file_path):
        """Upload a file to S3-compatible storage."""
        s3_object_key = os.path.relpath(
            local_file_path, self.local_directory
        )  # Remove local path prefix
        s3_object_key = os.path.join(self.s3_prefix, s3_object_key).replace(
            "\\", "/"
        )  # Format for S3
        print(f"Uploading {local_file_path} to S3 as {s3_object_key}...")
        try:
            self.s3_client.upload_file(local_file_path, self.s3_bucket, s3_object_key)
        except Exception as e:
            print(f"Upload failed for {local_file_path}: {e}")

    def delete_file_from_s3(self, local_file_path):
        """Delete a file from S3-compatible storage."""
        s3_object_key = os.path.relpath(local_file_path, self.local_directory)
        s3_object_key = os.path.join(self.s3_prefix, s3_object_key).replace("\\", "/")
        print(f"Deleting {s3_object_key} from S3...")
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_object_key)
        except Exception as e:
            print(f"Delete failed for {s3_object_key}: {e}")

    def on_created(self, event):
        if event.is_directory:
            return
        with self.lock:
            self.pending_uploads.add(event.src_path)
            self.pending_deletions.discard(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        with self.lock:
            self.pending_uploads.add(event.src_path)
            self.pending_deletions.discard(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        with self.lock:
            self.pending_deletions.add(event.src_path)
            self.pending_uploads.discard(event.src_path)
