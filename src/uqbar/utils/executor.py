# SPDX-License-Identifier: MIT
# uqbar/utils/utils.py
"""
Uqbar | Utils | Utils
=============

Overview
--------
Placeholder.

Metadata
--------
- Project: Uqbar
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

import subprocess
from typing import TextIO

# Type aliases for backwards compatibility
List = list
Tuple = tuple

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def execute_multiple(
    command_list: List[str],
    *,
    multiple_sessions: bool = True,
    join_string: str = " ; ",
    **kwargs,
) -> Tuple[str, str]:
    """
    Execute a list of shell commands sequentially in the same session.

    Args:
        command_list: A list of shell commands as strings.

    Returns:
        A tuple (stdout, stderr) containing the combined output and error messages.

    - Join commands with " && " or " ; ":
      " && " stops execution on failure; " ; " executes all regardless
    """
    # Join commands with "&&" or ";"
    # "&&" stops execution on failure; ";" executes all regardless
    " ; ".join(command_list)
    pass


def execute(
    full_command: str | list[str],
    *,
    stdout: int | TextIO | None = None,
    stderr: int | TextIO | None = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    shell: bool = False,
    env: bool | None = None,
    executable: str | None = "/bin/bash",
    split_string: str = " ",
    join_string: str = " ; ",
) -> tuple[str | None, str | None]:
    """
    Execute a single shell command.

    class subprocess.Popen(
        args, bufsize=-1, executable=None, stdin=None, stdout=None, stderr=None,
        preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None,
        universal_newlines=None, startupinfo=None, creationflags=0,
        restore_signals=True, start_new_session=False, pass_fds=(), *, group=None,
        extra_groups=None, user=None, umask=-1, encoding=None, errors=None,
        text=None, pipesize=-1, process_group=None
    )

    env={"PATH": "/usr/bin", "MYVAR": "42"}

    Implementation Notes
    --------------------
    stdout and stderr are Emums which can be:
    `None` (default)
    `subprocess.subprocess.PIPE`
    `subprocess.subprocess.STDOUT`
    `subprocess.subprocess.DEVNULL`
    `TextIO`
    """
    command: str | list[str] = full_command
    if isinstance(full_command, str):

        if not shell:
            # Split command
            command: list[str] = full_command.strip().split(split_string)

    if isinstance(full_command, list):

        if shell:
            # Join string
            temp_vec: list[str] = [e.strip() for e in full_command]
            command: str = join_string.join(temp_vec).strip()

    # Run in a single shell session
    # Note: Popen doesn't support capture_output, so we set
    # stdout/stderr to PIPE if capture_output is True
    if capture_output and stdout is None and stderr is None:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    process: subprocess.Popen | None = subprocess.Popen(
        command,
        stdout = stdout,
        stderr = stderr,
        text = text,
        encoding="utf-8",
        shell = shell,
        env = env,
        executable=executable,
    )
    stdout, stderr = process.communicate()

    if stdout and stderr:
        return str(stdout).strip(), str(stderr).strip()
    elif stdout:
        return str(stdout).strip(), None
    return None, None

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "execute_multiple",
    "execute",
]
