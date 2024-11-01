import ast
import inspect
import textwrap
from pathlib import Path
from dbgpy import config
from warnings import warn


def get_frame_above():
    frame = inspect.currentframe()
    outer_frame = inspect.getouterframes(frame)[2][
        0
    ]  # Move two up the stack since this is called from the child frame
    return outer_frame


def _get_func_obj(frame):
    """
    Get function object from a frame. If it can't find it, return None
    """

    codename = frame.f_code.co_name
    fobj = None

    try:
        if "self" in frame.f_locals:  # regular method
            fobj = getattr(frame.f_locals["self"].__class__, codename)
        elif "cls" in frame.f_locals:  # class method
            fobj = getattr(frame.f_locals["cls"], codename)
        else:
            module = inspect.getmodule(frame)  # only fetch module if we need it

            if hasattr(module, codename):  # regular module level function
                fobj = getattr(module, codename)
            else:  # static method
                classes = [
                    getattr(module, name)
                    for name in dir(module)
                    if inspect.isclass(getattr(module, name))
                ]
                for cls in classes:
                    if (
                        hasattr(cls, codename)
                        and getattr(cls, codename).__code__ == frame.f_code
                    ):
                        fobj = getattr(cls, codename)
                        break
        if fobj is None:
            """it's likely some nested function/method or a lambda, who logs in a lambda?"""
            return None
        return fobj
    except Exception:
        """never break logging"""
        return None


def _get_call_args_from_frame(frame):
    """Get AST nodes for each argument in the function call."""
    frame_info = inspect.getframeinfo(frame)

    # Line number of this function call
    line_number = frame_info.lineno

    # Line number of parent function definition
    parent_line_number = frame.f_code.co_firstlineno

    # Get the function calling this function
    calling_function = _get_func_obj(frame)

    # Parse the function to an ast
    calling_source, function_ast = _parse_ast(calling_function, frame)
    if calling_source is None and function_ast is None:
        return None, None, None

    assert function_ast is not None

    # Line number of this function call
    function_call_line_number = line_number - parent_line_number + 1

    # Find the call object in the function ast matching the line number
    call_object: ast.Call | None = None

    for node in ast.walk(function_ast):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if node.lineno == function_call_line_number:
                call_object = node.value
                break
    assert call_object is not None
    # Get the call object's arguments
    call_args = call_object.args

    return call_args, calling_source, parent_line_number - 1


def _parse_ast(calling_function, frame):
    if frame.f_code.co_filename == "<stdin>":
        warn(
            "Cannot get source from stdin (for example in Python REPL), dbg will default to printing normally",
            stacklevel=2,
        )
        return None, None
    elif "<cell line: " in frame.f_code.co_name:
        warn(
            "dbg currently doesn't support IPython cells, dbg will default to printing normally",
            stacklevel=2,
        )
        return None, None
    elif calling_function is None:
        # In a module
        calling_source = inspect.getsource(frame)
        # Unindent the source
        calling_source = textwrap.dedent(calling_source)
        function_ast = ast.parse(calling_source)
    else:
        # In a function we just need to parse the function
        calling_source = inspect.getsource(calling_function)
        # Unindent the source
        calling_source = textwrap.dedent(calling_source)
        function_ast = ast.parse(calling_source)
    return calling_source, function_ast


def frame_file_path(frame):
    """
    Return the path of the frame
    """
    try:
        if config.project_path:
            return Path(frame.f_code.co_filename).relative_to(Path.cwd())
        else:
            return Path(frame.f_code.co_filename).name
    except ValueError:
        return "<unknown>"
