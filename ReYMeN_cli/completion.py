# -*- coding: utf-8 -*-
"""ReYMeN_cli/completion.py — Shell Completion.

Bash/Zsh/PowerShell icin tab completion.
"""

_SHELL_KOMUTLAR = [
    "run", "serve", "doctor", "version",
    "skill list", "skill search", "skill add", "skill remove", "skill detail", "skill stats",
    "skill bundle create", "skill bundle load",
    "skill hub list", "skill hub download",
    "provider list", "provider test", "provider switch", "provider ping",
    "model list", "model detail", "model recommend", "model benchmark",
    "kanban list", "kanban add", "kanban move", "kanban remove", "kanban stats",
    "mcp list", "mcp serve", "mcp test", "mcp config",
    "mcp catalog list", "mcp catalog detail",
    "profile list", "profile create", "profile switch", "profile current",
    "config show", "config set",
    "cron list", "cron add", "cron remove",
    "gateway start", "gateway stop", "gateway status",
    "memory show", "memory search",
]


def completion_bash() -> str:
    """Bash completion scripti."""
    komutlar = " ".join(_SHELL_KOMUTLAR)
    return (
        "# ReYMeN Bash Completion\n"
        "_reyment_completion() {\n"
        '    local cur="${COMP_WORDS[COMP_CWORD]}"\n'
        '    local prev="${COMP_WORDS[COMP_CWORD-1]}"\n'
        "    COMPREPLY=( $(compgen -W \"" + komutlar + '" -- "$cur") )\n'
        "    return 0\n"
        "}\n"
        "complete -F _reyment_completion reyment.py\n"
    )


def completion_zsh() -> str:
    """Zsh completion scripti."""
    komut_satiri = "'" + "' '".join(_SHELL_KOMUTLAR) + "'"
    return (
        "#compdef reyment.py\n"
        "_reyment_completion() {\n"
        "    local -a commands\n"
        "    commands=(\n"
        "        " + komut_satiri + "\n"
        "    )\n"
        "    _describe 'command' commands\n"
        "}\n"
        "_reyment_completion \"$@\"\n"
    )


def completion_powershell() -> str:
    """PowerShell completion scripti."""
    komutlar = "', '".join(_SHELL_KOMUTLAR)
    return (
        "# ReYMeN PowerShell Completion\n"
        "Register-ArgumentCompleter -Native -CommandName reyment.py -ScriptBlock {\n"
        "    param($wordToComplete, $commandAst, $cursorPosition)\n"
        "    $commands = @('" + komutlar + "')\n"
        '    $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object { $_ }\n'
        "}\n"
    )


def completion_install(shell: str = "bash") -> str:
    """Completion scriptini kaydet ve yuklenmesini soyle."""
    scripts = {
        "bash": ("~/.bashrc", completion_bash()),
        "zsh": ("~/.zshrc", completion_zsh()),
        "powershell": ("$PROFILE", completion_powershell()),
    }
    if shell not in scripts:
        return f"[Completion] Desteklenmeyen shell: {shell}"

    dosya, icerik = scripts[shell]
    return (
        f"[Completion] {shell} icin completion hazir.\n"
        f"  Kopyala: echo '$(cat {dosya} 2>/dev/null)' > {dosya}\n"
        f"  Veya su scripti ~/.bashrc'ye ekle:\n\n{icerik}"
    )
