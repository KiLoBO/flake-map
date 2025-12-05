from pathlib import Path
from typing import List, Optional


class flakeIndex:
    """Flake discovery and index of *.nix files"""

    def __init__(self, startDir: Optional[Path] = None):
        self.startDir = startDir
        self.flakeRoot: Optional[Path] = None
        self.flakePath: Optional[Path] = None

    def initialize(self) -> bool:
        """
        Find and initialize the flake root.

        Returns:
            True if flake was found, False otherwise
        """
        self.flakeRoot = self._getFlakeRoot(self.startDir)

        if self.flakeRoot:
            self.flakePath = self.flakeRoot / "flake.nix"
            return True

        return False

    def _getFlakeRoot(self, startDir: Optional[Path] = None) -> Optional[Path]:
        """
        Find flake.nix in the specificied directory or parent directories.

        Args:
            startDir: directory to start searching from

        Returns:
            Path to dir containing flake.nix, or None if not found
        """
        current = Path(startDir) if startDir else Path.cwd()

        for _ in range(5):
            if (current / "flake.nix").exists():
                return current
            if current == current.parent:
                break
            current = current.parent

        return None

    def getNixFiles(self) -> List[Path]:
        """
        Get all .nix files in the flake.

        Returns:
           List of path objects for .nix files
        """
        if not self.flakeRoot:
            return []

        return [
            f
            for f in self.flakeRoot.rglob("*.nix")
            if not any(part.startswith(".") for part in f.parts)
        ]
