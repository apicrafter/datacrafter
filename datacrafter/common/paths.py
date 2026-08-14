"""Path helpers for trusted project scripts."""
import os


def resolve_project_script(project_path, script_path):
    """Resolve a script path and require it to live under the project directory.

    Configuration and custom ``code`` scripts are trusted (they execute via
    ``runpy``), but they must still resolve inside the project tree so a YAML
    value cannot point at an arbitrary file outside the project.
    """
    if not script_path:
        raise ValueError("Script path is required")
    if not project_path:
        raise ValueError("Project path is required to resolve a script")

    project_root = os.path.realpath(project_path)
    if os.path.isabs(script_path):
        resolved = os.path.realpath(script_path)
    else:
        resolved = os.path.realpath(os.path.join(project_root, script_path))

    try:
        inside_project = os.path.commonpath([project_root, resolved]) == project_root
    except ValueError:
        # Different drives on Windows, or empty paths.
        inside_project = False

    if not inside_project:
        raise ValueError(
            f"Script {script_path!r} must live under the project directory "
            f"{project_root}")

    if not os.path.isfile(resolved):
        raise ValueError(f"Script not found: {script_path}")

    return resolved
