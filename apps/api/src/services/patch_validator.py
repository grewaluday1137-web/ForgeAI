import logging
import ast
from typing import Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class PatchValidator:
    """
    Validates generated patches for syntax correctness and security.
    """
    
    def validate(self, generated_json: dict, repo_path: Path) -> Tuple[bool, list[str]]:
        errors = []
        
        # 1. Validate JSON structure
        if "patches" not in generated_json and "new_files" not in generated_json and "deleted_files" not in generated_json:
            return False, ["Invalid schema: No patches, new_files, or deleted_files found."]
            
        # 2. Validate Patches
        for patch in generated_json.get("patches", []):
            file_path = patch.get("file_path")
            diff = patch.get("diff")
            
            if not file_path or not diff:
                errors.append("Patch missing file_path or diff.")
                continue
                
            # Security: Path traversal check
            if ".." in file_path or file_path.startswith("/"):
                errors.append(f"Invalid file path: {file_path}")
                continue
                
            full_path = repo_path / file_path
            if not full_path.exists():
                errors.append(f"Target file does not exist: {file_path}")
                
            # Basic diff sanity check
            if not diff.startswith("---") or "+++" not in diff:
                errors.append(f"Invalid unified diff format for {file_path}")

        # 3. Validate New Files
        for new_file in generated_json.get("new_files", []):
            file_path = new_file.get("file_path")
            content = new_file.get("content")
            
            if not file_path or content is None:
                errors.append("New file missing file_path or content.")
                continue
                
            if ".." in file_path or file_path.startswith("/"):
                errors.append(f"Invalid file path: {file_path}")
                continue
                
            # Syntax check if Python
            if file_path.endswith(".py"):
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append(f"Syntax error in new file {file_path}: {e}")
                    
        # 4. Validate Deleted Files
        for file_path in generated_json.get("deleted_files", []):
            if ".." in file_path or file_path.startswith("/"):
                errors.append(f"Invalid file path: {file_path}")
                
            full_path = repo_path / file_path
            if not full_path.exists():
                errors.append(f"Cannot delete non-existent file: {file_path}")
                
        return len(errors) == 0, errors

patch_validator = PatchValidator()
