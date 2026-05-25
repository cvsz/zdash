```markdown
# zdash Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `zdash` Python codebase. You'll learn how to structure files, write imports and exports, follow commit message styles, and understand the testing approach. This guide is ideal for contributors looking to maintain consistency and quality in the project.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files.
  - Example: `data_loader.py`, `user_profile_manager.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_config
    from ..models import User
    ```

### Export Style
- Use **named exports** (explicitly define what is exported from modules).
  - Example:
    ```python
    __all__ = ["parse_config", "User"]
    ```

### Commit Messages
- No strict format, but commonly prefixed with `phase4`.
- Keep messages concise (average 47 characters).
  - Example: `phase4: add user authentication handler`

## Workflows

### Adding a New Module
**Trigger:** When you need to introduce new functionality.
**Command:** `/add-module`

1. Create a new Python file using snake_case (e.g., `feature_x.py`).
2. Use relative imports to bring in dependencies from within the package.
   ```python
   from .utils import helper_function
   ```
3. Define `__all__` to specify exported functions/classes.
   ```python
   __all__ = ["FeatureX"]
   ```
4. Write concise commit messages, optionally prefixed with `phase4`.
5. Add or update corresponding test files (see Testing Patterns).

### Writing Tests
**Trigger:** When adding or updating code.
**Command:** `/write-test`

1. Create a test file matching the pattern `*.test.*` (e.g., `feature_x.test.py`).
2. Place test files alongside the modules they test or in a dedicated test directory.
3. Use your preferred testing framework (none detected, so choose as appropriate).
4. Write tests for all public functions and classes.
5. Run tests before committing changes.

## Testing Patterns

- Test files follow the pattern `*.test.*` (e.g., `module.test.py`).
- No specific testing framework detected; choose one that fits your workflow (e.g., `unittest`, `pytest`).
- Place tests in files named after the module being tested.
- Example test file structure:
  ```python
  # feature_x.test.py
  import unittest
  from .feature_x import FeatureX

  class TestFeatureX(unittest.TestCase):
      def test_feature(self):
          self.assertTrue(FeatureX().do_something())
  ```

## Commands
| Command        | Purpose                                   |
|----------------|-------------------------------------------|
| /add-module    | Scaffold a new module with conventions    |
| /write-test    | Create and structure a new test file      |
```
