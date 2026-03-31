"""
SMARTHAUS M365 Server — formal application entry point.

Launches the M365 ops adapter as a production-style server. No Makefile or
dev environment required. Use Python 3.14+.

  m365-server              # headless, port from env or 9000
  m365-server --port 9000
  m365-server --gui        # window with status and Quit
  python -m m365_server
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
from pathlib import Path

from smarthaus_common.config import load_bootstrap_env


def _find_app_root() -> Path:
    """Resolve app root: M365_APP_ROOT env, or cwd with registry/, or cwd."""
    root_env = os.getenv("M365_APP_ROOT")
    if root_env:
        p = Path(root_env).resolve()
        if p.is_dir():
            return p
    cwd = Path.cwd()
    if (cwd / "registry" / "agents.yaml").exists():
        return cwd
    if (cwd / "src" / "ops_adapter").exists():
        return cwd
    return cwd


def _tenant_search_dirs(app_root: Path) -> list[Path]:
    dirs: list[Path] = []
    ucp_root = os.getenv("UCP_ROOT")
    repos_root = os.getenv("REPOS_ROOT") or os.getenv("UCP_REPOS_ROOT")
    if ucp_root:
        dirs.append((Path(ucp_root) / "tenants").resolve())
    if repos_root:
        dirs.append((Path(repos_root) / "SMARTHAUS_MCPSERVER_core" / "tenants").resolve())
    dirs.append((app_root.parent / "UCP" / "tenants").resolve())
    dirs.append((app_root.parent / "SMARTHAUS_MCPSERVER_core" / "tenants").resolve())
    return dirs


def _discover_bootstrap_tenant(app_root: Path) -> str | None:
    explicit_default = os.getenv("M365_DEFAULT_TENANT", "").strip()
    if explicit_default:
        return explicit_default

    candidates: set[str] = set()
    for tenant_dir in _tenant_search_dirs(app_root):
        if not tenant_dir.is_dir():
            continue
        for yaml_path in tenant_dir.glob("*.yaml"):
            name = yaml_path.name
            if name.startswith((".", "_")):
                continue
            candidates.add(yaml_path.stem)

    if "smarthaus" in candidates:
        return "smarthaus"
    if len(candidates) == 1:
        return next(iter(candidates))
    return None


def _load_env(app_root: Path) -> None:
    """Load .env from app root or ~/.smarthaus/m365 if present."""
    load_bootstrap_env(
        app_root / ".env",
        Path.home() / ".smarthaus" / "m365" / ".env",
    )
    if not os.getenv("UCP_TENANT", "").strip():
        bootstrap_tenant = _discover_bootstrap_tenant(app_root)
        if bootstrap_tenant:
            os.environ["UCP_TENANT"] = bootstrap_tenant


def _run_server(host: str, port: int, app_root: Path) -> None:
    """Set env for registry/logs and run uvicorn."""
    registry = app_root / "registry" / "agents.yaml"
    if registry.exists():
        os.environ["REGISTRY_FILE"] = str(registry.resolve())
    log_dir = app_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    os.environ["LOG_DIR"] = str(log_dir.resolve())

    import uvicorn
    from ops_adapter.main import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )


def _run_gui(host: str, port: int, app_root: Path) -> None:
    """Run server in a background thread and show a simple status window."""
    import tkinter as tk
    from tkinter import font as tkfont

    server_thread: threading.Thread | None = None
    server_started = threading.Event()

    def run_server() -> None:
        _run_server(host, port, app_root)

    def start_server() -> None:
        nonlocal server_thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        server_started.set()

    root = tk.Tk()
    root.title("SMARTHAUS M365 Server")
    root.minsize(400, 180)
    root.resizable(True, True)

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11)
    title_font = tkfont.Font(family=default_font.cget("family"), size=14, weight="bold")

    frame = tk.Frame(root, padx=24, pady=24)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="SMARTHAUS M365 Server", font=title_font).pack(pady=(0, 8))
    tk.Label(frame, text="Ops adapter and agent control API", fg="gray").pack(pady=(0, 16))

    url = f"http://{host}:{port}"
    url_label = tk.Label(frame, text=url, font=("Menlo", 12), fg="blue", cursor="hand2")
    url_label.pack(pady=(0, 8))

    def copy_url(_event: object) -> None:
        root.clipboard_clear()
        root.clipboard_append(url)

    url_label.bind("<Button-1>", copy_url)

    status_var = tk.StringVar(value="Starting…")
    tk.Label(frame, textvariable=status_var, fg="gray").pack(pady=(0, 20))

    def on_quit() -> None:
        root.destroy()
        os._exit(0)

    tk.Button(frame, text="Quit", command=on_quit, width=12, height=1).pack(pady=(0, 8))

    def update_status() -> None:
        if server_started.is_set():
            status_var.set("Server is running. Use Quit to stop.")

    root.after(500, start_server)
    root.after(1500, update_status)
    root.protocol("WM_DELETE_WINDOW", on_quit)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SMARTHAUS M365 Server — launch the M365 ops adapter.",
        prog="m365-server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("M365_SERVER_PORT", "9000")),
        help="Port to bind (default: 9000 or M365_SERVER_PORT)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("M365_SERVER_HOST", "0.0.0.0"),
        help="Host to bind (default: 0.0.0.0 or M365_SERVER_HOST)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Show a simple window with status and Quit button",
    )
    args = parser.parse_args()

    if sys.version_info < (3, 14):
        print("SMARTHAUS M365 Server requires Python 3.14 or newer.", file=sys.stderr)
        sys.exit(1)

    app_root = _find_app_root()
    _load_env(app_root)

    registry = app_root / "registry" / "agents.yaml"
    if not registry.exists():
        print(
            f"Registry not found at {registry}. Run from the M365 repo root or set M365_APP_ROOT.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.gui:
        _run_gui(args.host, args.port, app_root)
    else:
        _run_server(args.host, args.port, app_root)


if __name__ == "__main__":
    main()
