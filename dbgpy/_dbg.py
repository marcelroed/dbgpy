from typing import Any, List, Optional
import ast

from dbgpy._stack_inspect import (
    get_frame_above,
    _get_call_args_from_frame,
    frame_file_path,
)
from dbgpy import config

try:
    import torch
except ImportError:
    torch = None

try:
    import astunparse
except ImportError:
    astunparse = None

__all__ = ["dbg"]


def _space_all_but_first(s: str, n_spaces: int) -> str:
    """Pad all lines except the first with n_spaces spaces"""
    lines = s.splitlines()
    for i in range(1, len(lines)):
        lines[i] = " " * n_spaces + lines[i]
    return "\n".join(lines)


def _format_value(val: Any, _repr=False):
    # Guards for special types
    if torch is not None and isinstance(val, torch.Tensor) and not _repr:
        val_string = str(val)
        end_of_tensor = val_string.rfind(")")
        new_val_string = f"{val_string[:end_of_tensor]}, shape={val.shape}{val_string[end_of_tensor:]}"
        return new_val_string

    # Otherwise, default to repr or str
    if _repr or isinstance(val, str):
        return repr(val)
    return str(val)


def _print_spaced(prefix: str, val_str: str, **kwargs):
    """Print variables with their variable names"""
    n_spaces = len(prefix)
    spaced = _space_all_but_first(val_str, n_spaces)
    print(
        f"{prefix} {spaced}",
        **kwargs,
    )


def _format_prefix(
    file_path: str, lineno: int, expression_string: Optional[str], val: Any
):
    inner_path = f"{file_path}:{lineno}"
    path = config.prefix_format.format(path=inner_path)

    # Use expression only if expression is not a literal string
    return f"{path} {expression_string} =" if expression_string else f"{path}"


def _get_expression(call_source_lines: List[str], arg) -> Optional[str]:
    if isinstance(arg, (ast.Constant, ast.JoinedStr)):
        return None

    # If multiline expression, clean up using ast.unparse (or astunparse)
    if arg.lineno != arg.end_lineno:
        if hasattr(ast, "unparse"):  # If in version 3.9 or newer
            return ast.unparse(arg)
        else:  # Otherwise, use astunparse
            return astunparse.unparse(arg)

    # Otherwise, just return the literal expression string
    return call_source_lines[arg.lineno - 1][
        arg.col_offset : arg.end_col_offset
    ].strip()


def dbg(*vals, **kwargs):
    """
    Debug output with expression and value
    """
    outer_frame = get_frame_above()

    # Parse the stack frame, return source and arg nodes
    call_args, call_source, base_lineno = _get_call_args_from_frame(outer_frame)
    call_source_lines = call_source.splitlines()

    assert len(call_args) == len(vals)

    for arg, val in zip(call_args, vals):
        expression = _get_expression(call_source_lines, arg)
        prefix = _format_prefix(
            frame_file_path(outer_frame), arg.lineno + base_lineno, expression, val
        )
        val_str = _format_value(val)
        _print_spaced(prefix, val_str)

    return vals
