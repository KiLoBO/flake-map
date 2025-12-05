from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree

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
        # yield ListView(id="output")
        yield Tree("Flake Files", id="file-tree")
        yield Footer()

    def on_mount(self) -> None:
        """Index flake on app start"""
        if not self.flake_index.initialize():
            self.notify("Flake not found in CWD. Specify a path", severity="error")
            self.exit()
            return

        self.notify(f"Flake found: {self.flake_index.flakePath}")
        self.refreshFileTree()

    def refreshFileTree(self) -> None:
        """Populate the file tree structure."""
        nixFiles = self.flake_index.getNixFiles()

        tree = self.query_one("#file-tree", Tree)
        tree.clear()

        # Set root label to flake directory name
        tree.label = f"📁 {self.flake_index.flakeRoot.name}"
        tree.root.expand()

        # Build directory structure
        dir_nodes = {}  # Cache for directory nodes

        for file in sorted(nixFiles):
            relPath = file.relative_to(self.flake_index.flakeRoot)
            parts = relPath.parts

            # Build directory hierarchy
            current_node = tree.root
            current_path = Path()

            # Create intermediate directory nodes
            for part in parts[:-1]:  # All except the filename
                current_path = current_path / part
                path_str = str(current_path)

                if path_str not in dir_nodes:
                    # Create new directory node
                    dir_node = current_node.add(f"📁 {part}", expand=False)
                    dir_nodes[path_str] = dir_node
                    current_node = dir_node
                else:
                    current_node = dir_nodes[path_str]

            # Add the file to its parent directory
            filename = parts[-1]
            file_node = current_node.add_leaf(f"📄 {filename}")
            file_node.data = file

        self.notify(f"Found {len(nixFiles)} .nix files")

    def action_refresh(self) -> None:
        """Refresh file tree"""
        self.refreshFileTree()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle file selection"""
        if event.node.data:
            selFilePath = event.node.data
            self.notify(f"Selected: {selFilePath}")


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
