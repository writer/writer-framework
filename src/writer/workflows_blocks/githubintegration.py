import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from github import Github, GithubException
import base64
import requests
from pathlib import Path

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class GitHubIntegration(WorkflowBlock):
    def __init__(self):
        super().__init__()
        self.github = None
        
    @classmethod
    def register(cls, type: str):
        super(GitHubIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "GitHub Integration",
                "description": "Execute GitHub operations and manage repositories",
                "category": "Version Control",
                "fields": {
                    "token": {
                        "name": "Access Token",
                        "type": "Text",
                        "description": "GitHub Personal Access Token"
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            # Repository Operations
                            "create_repo": "Create Repository",
                            "delete_repo": "Delete Repository",
                            "list_repos": "List Repositories",
                            "get_repo_info": "Get Repository Info",
                            
                            # Branch Operations
                            "create_branch": "Create Branch",
                            "delete_branch": "Delete Branch",
                            "list_branches": "List Branches",
                            "protect_branch": "Protect Branch",
                            
                            # File Operations
                            "get_file_content": "Get File Content",
                            "create_file": "Create File",
                            "update_file": "Update File",
                            "delete_file": "Delete File",
                            
                            # Issue Operations
                            "create_issue": "Create Issue",
                            "update_issue": "Update Issue",
                            "list_issues": "List Issues",
                            "add_issue_comment": "Add Issue Comment",
                            
                            # Pull Request Operations
                            "create_pull_request": "Create Pull Request",
                            "list_pull_requests": "List Pull Requests",
                            "merge_pull_request": "Merge Pull Request",
                            "review_pull_request": "Review Pull Request",
                            
                            # Workflow Operations
                            "list_workflows": "List Workflows",
                            "trigger_workflow": "Trigger Workflow",
                            "get_workflow_runs": "Get Workflow Runs",
                            
                            # Release Operations
                            "create_release": "Create Release",
                            "list_releases": "List Releases",
                            
                            # Team Operations
                            "list_teams": "List Teams",
                            "add_team_member": "Add Team Member",
                            
                            # Project Operations
                            "create_project": "Create Project",
                            "list_projects": "List Projects"
                        },
                        "default": "list_repos"
                    },
                    "repo_name": {
                        "name": "Repository Name",
                        "type": "Text",
                        "description": "Name of the repository",
                        "required": False
                    },
                    "owner": {
                        "name": "Owner",
                        "type": "Text",
                        "description": "Repository owner (user/organization)",
                        "required": False
                    },
                    "branch": {
                        "name": "Branch",
                        "type": "Text",
                        "description": "Branch name",
                        "required": False
                    },
                    "file_path": {
                        "name": "File Path",
                        "type": "Text",
                        "description": "Path to file in repository",
                        "required": False
                    },
                    "content": {
                        "name": "Content",
                        "type": "Text",
                        "description": "Content for file/issue/PR operations",
                        "required": False
                    },
                    "title": {
                        "name": "Title",
                        "type": "Text",
                        "description": "Title for issue/PR/release",
                        "required": False
                    },
                    "body": {
                        "name": "Body",
                        "type": "Text",
                        "description": "Body content for issue/PR/release",
                        "required": False
                    },
                    "labels": {
                        "name": "Labels",
                        "type": "Text",
                        "description": "Labels as JSON array",
                        "default": "[]",
                        "required": False
                    },
                    "assignees": {
                        "name": "Assignees",
                        "type": "Text",
                        "description": "Assignees as JSON array",
                        "default": "[]",
                        "required": False
                    },
                    "commit_message": {
                        "name": "Commit Message",
                        "type": "Text",
                        "description": "Commit message for file operations",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation completed successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "An error occurred during the operation.",
                        "style": "error",
                    },
                    "auth_error": {
                        "name": "Authentication Error",
                        "description": "Authentication failed.",
                        "style": "error",
                    }
                },
            }
        ))

    def _initialize_client(self, token: str):
        """Initialize GitHub client"""
        try:
            self.github = Github(token)
            # Test authentication
            self.github.get_user().login
        except GithubException as e:
            self.outcome = "auth_error"
            raise RuntimeError(f"Authentication failed: {str(e)}")

    def _get_repo(self, owner: str, repo_name: str):
        """Get repository object"""
        try:
            return self.github.get_repo(f"{owner}/{repo_name}")
        except GithubException as e:
            self.outcome = "error"
            raise RuntimeError(f"Repository error: {str(e)}")

    def _create_repo(self, name: str, private: bool = False, description: str = None) -> Dict[str, Any]:
        """Create a new repository"""
        try:
            user = self.github.get_user()
            repo = user.create_repo(
                name=name,
                private=private,
                description=description
            )
            return {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "html_url": repo.html_url,
                "private": repo.private
            }
        except GithubException as e:
            self.outcome = "error"
            raise RuntimeError(f"Repository creation error: {str(e)}")

    def _list_repos(self, owner: str = None) -> Dict[str, Any]:
        """List repositories"""
        try:
            if owner:
                repos = self.github.get_user(owner).get_repos()
            else:
                repos = self.github.get_user().get_repos()
            
            return {
                "repositories": [{
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "html_url": repo.html_url,
                    "private": repo.private,
                    "description": repo.description
                } for repo in repos]
            }
        except GithubException as e:
            self.outcome = "error"
            raise RuntimeError(f"Repository listing error: {str(e)}")

    def _create_issue(self, repo, title: str, body: str, labels: List[str] = None, 
                     assignees: List[str] = None) -> Dict[str, Any]:
        """Create an issue"""
        try:
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels,
                assignees=assignees
            )
            return {
                "id": issue.id,
                "number": issue.number,
                "title": issue.title,
                "html_url": issue.html_url,
                "state": issue.state
            }
        except GithubException as e:
            self.outcome = "error"
            raise RuntimeError(f"Issue creation error: {str(e)}")

    def _create_pull_request(self, repo, title: str, body: str, head: str, 
                           base: str = "main") -> Dict[str, Any]:
        """Create a pull request"""
        try:
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            return {
                "id": pr.id,
                "number": pr.number,
                "title": pr.title,
                "html_url": pr.html_url,
                "state": pr.state
            }
        except GithubException as e:
            self.outcome = "error"
            raise RuntimeError(f"Pull request creation error: {str(e)}")

    def _file_operation(self, repo, operation: str, file_path: str, 
                       content: str = None, commit_message: str = None) -> Dict[str, Any]:
        """Handle file operations"""
        try:
            if operation == "get":
                contents = repo.get_contents(file_path)
                content = base64.b64decode(contents.content).decode('utf-8')
                return {
                    "content": content,
                    "sha": contents.sha,
                    "size": contents.size
                }
            elif operation == "create":
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content
                )
                return {
                    "commit": {
                        "sha": result["commit"].sha,
                        "message": result["commit"].message
                    },
                    "content": {
                        "path": result["content"].path,
                        "sha": result["content"].sha
                    }
                }
            elif operation == "update":
                contents = repo.get_contents(file_path)
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=contents.sha
                )
                return {
                    "commit": {
                        "sha": result["commit"].sha,
                        "message": result["commit"].message
                    },
                    "content": {
                        "path": result["content"].path,
                        "sha": result["content"].sha
                    }
                }
            elif operation == "delete":
                contents = repo.get_contents(file_path)
                result = repo.delete_file(
                    path=file_path,
                    message=commit_message,
                    sha=contents.sha
                )
                return {
                    "commit": {
                        "sha": result["commit"].sha,
                        "message": result["commit"].message
                    }
                }
        except GithubException as e:
            self.outcome = "error"
            raise RuntimeError(f"File operation error: {str(e)}")

    def run(self):
        try:
            # Get authentication token
            token = self._get_field("token")
            self._initialize_client(token)

            # Get operation details
            operation = self._get_field("operation")
            repo_name = self._get_field("repo_name", True)
            owner = self._get_field("owner", True)
            branch = self._get_field("branch", True)
            file_path = self._get_field("file_path", True)
            content = self._get_field("content", True)
            title = self._get_field("title", True)
            body = self._get_field("body", True)
            labels = json.loads(self._get_field("labels", True, "[]"))
            assignees = json.loads(self._get_field("assignees", True, "[]"))
            commit_message = self._get_field("commit_message", True)

            # Execute requested operation
            if operation == "create_repo":
                result = self._create_repo(
                    name=repo_name,
                    description=body
                )
            
            elif operation == "list_repos":
                result = self._list_repos(owner)
            
            elif operation in ["create_issue", "create_pull_request", "get_file_content", 
                             "create_file", "update_file", "delete_file"]:
                repo = self._get_repo(owner, repo_name)
                
                if operation == "create_issue":
                    result = self._create_issue(
                        repo=repo,
                        title=title,
                        body=body,
                        labels=labels,
                        assignees=assignees
                    )
                    
                elif operation == "create_pull_request":
                    result = self._create_pull_request(
                        repo=repo,
                        title=title,
                        body=body,
                        head=branch
                    )
                    
                elif operation == "get_file_content":
                    result = self._file_operation(
                        repo=repo,
                        operation="get",
                        file_path=file_path
                    )
                    
                elif operation == "create_file":
                    result = self._file_operation(
                        repo=repo,
                        operation="create",
                        file_path=file_path,
                        content=content,
                        commit_message=commit_message
                    )
                    
                elif operation == "update_file":
                    result = self._file_operation(
                        repo=repo,
                        operation="update",
                        file_path=file_path,
                        content=content,
                        commit_message=commit_message
                    )
                    
                elif operation == "delete_file":
                    result = self._file_operation(
                        repo=repo,
                        operation="delete",
                        file_path=file_path,
                        commit_message=commit_message
                    )
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Store result and set success outcome
            self.result = {
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "data": result
            }
            self.outcome = "success"

        except ValueError as e:
            self.outcome = "error"
            raise RuntimeError(f"Validation error: {str(e)}")
        except Exception as e:
            if not self.outcome:
                self.outcome = "error"
            raise RuntimeError(f"Operation error: {str(e)}")

