import os
import subprocess
import logging
from pathlib import Path
from git import Repo
from src.services.git import git_service

logger = logging.getLogger(__name__)

class PatchApplier:
    """
    Applies validated patches to the local filesystem and commits them via Git.
    """
    
    def apply(self, generated_json: dict, owner: str, repo_name: str, commit_message: str) -> str:
        repo_path = git_service._get_repo_path(owner, repo_name)
        
        # 1. Apply diffs
        for patch in generated_json.get("patches", []):
            file_path = patch["file_path"]
            diff = patch["diff"]
            
            # Write diff to a temp file
            diff_path = repo_path / f"temp_{os.urandom(4).hex()}.patch"
            with open(diff_path, "w", encoding="utf-8") as f:
                f.write(diff + "\n")
                
            try:
                # Apply using system patch command (must run inside the repo)
                result = subprocess.run(
                    ["patch", "-p0", "-i", diff_path.name],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise Exception(f"Failed to apply patch to {file_path}: {result.stderr}")
            finally:
                if diff_path.exists():
                    os.remove(diff_path)
                    
        # 2. Write New Files
        for new_file in generated_json.get("new_files", []):
            full_path = repo_path / new_file["file_path"]
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_file["content"])
                
        # 3. Delete Files
        for del_file in generated_json.get("deleted_files", []):
            full_path = repo_path / del_file
            if full_path.exists():
                os.remove(full_path)
                
        # 4. Commit via Git
        try:
            repo = Repo(repo_path)
            repo.git.add(all=True)
            if not repo.index.diff("HEAD"):
                logger.info("No changes to commit after applying patch.")
                return repo.head.commit.hexsha
                
            commit = repo.index.commit(commit_message)
            logger.info(f"Committed changes: {commit.hexsha}")
            
            # Optional: push to remote if PAT is present (for Milestone 7)
            # origin = repo.remote(name='origin')
            # origin.push()
            
            return commit.hexsha
        except Exception as e:
            logger.error(f"Git commit failed: {e}")
            raise

patch_applier = PatchApplier()
