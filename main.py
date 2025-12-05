from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label

from typing import ClassVar, Optional
from pathlib import Path
import argparse
from flakeIndex import flakeIndex


class NixFlakeMapper(App):
    CSS_PATH: ClassVar[str] = "main.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, flakeDir: Optional[Path] = None):
        super().__init__()
        self.flake_index = flakeIndex(flakeDir)

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield ListView(id="output")
        yield Footer()

    def on_mount(self) -> None:
        """Index flake on app start"""
        if not self.flake_index.initialize():
            self.notify("Flake not found in CWD. Specify a path", severity="error")
            self.exit()
            return

        self.notify(f"Flake foundL {self.flake_index.flakePath}")
        self.refreshFileList()

    def refreshFileList(self) -> None:
        """Refresh the list of .nix files. (r)"""
        nixFiles = self.flake_index.getNixFiles()

        listView = self.query_one("#output", ListView)
        listView.clear()

        for file in sorted(nixFiles):
            relPath = file.relative_to(self.flake_index.flakeRoot)
            listView.append(ListItem(Label(str(relPath))))

        self.notify(f"Found {len(nixFiles)} .nix files")

    def action_refresh(self) -> None:
        """Refresh file list"""
        self.refreshFileList()


def main():
    parser = argparse.ArgumentParser(
        description="Inspect NixOS flake configuration files"
    )
    parser.add_argument("flakeDir", nargs="?", default=None, help="Path to flake dir")

    args = parser.parse_args()

    flakeDir = Path(args.flakeDir).expanduser() if args.flakeDir else None

    app = NixFlakeMapper(flakeDir)
    app.run()


if __name__ == "__main__":
    main()
