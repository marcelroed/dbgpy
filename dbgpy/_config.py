from attr import attrs

__all__ = ["config"]


@attrs(auto_attribs=True)
class _Config:
    """Global mutable configuration object for dbgpy"""

    project_path: bool = True
    """Print the file path relative to the project root"""

    prefix_format: str = "{path}:"
    """Format string for the prefix of the debug output. `path` is the path of the file."""


config = _Config()
