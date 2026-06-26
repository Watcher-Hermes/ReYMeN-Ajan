"""
tools.environments — Terminal arka uç ortamları.

Kullanılabilir ortamlar:
- local: Yerel Windows/POSIX
- ssh: Uzak sunucu (paramiko)
- docker: Docker konteyner (SDK/CLI)
- wsl: WSL Linux (Windows)
"""

from reymen.hermes.tools.environments.base import BaseEnvironment
from reymen.hermes.tools.environments.local import LocalEnvironment
from reymen.hermes.tools.environments.ssh import SSHEnvironment
from reymen.hermes.tools.environments.docker import DockerEnvironment

try:
    from reymen.hermes.tools.environments.wsl import WSLEnvironment
    HAS_WSL = True
except ImportError:
    HAS_WSL = False

__all__ = [
    "BaseEnvironment",
    "LocalEnvironment",
    "SSHEnvironment",
    "DockerEnvironment",
]
if HAS_WSL:
    __all__.append("WSLEnvironment")
