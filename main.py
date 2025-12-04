from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Placeholder

from typing import ClassVar


class testApp(App):
    CSS_PATH: ClassVar[str] = "main.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Placeholder()
        yield Footer()


if __name__ == "__main__":
    app = testApp()
    app.run()
