"""
Logging utility with rich console output and file logging.
Provides structured logging for the migration tool.
"""

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

from config.settings import settings

# Custom theme for rich console
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "debug": "blue",
})

console = Console(theme=custom_theme)


class Logger:
    """Logger class with rich console and file output."""

    def __init__(self, name: str = "legacy_migration_tool"):
        """Initialize logger with name."""
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup logger with handlers and formatters."""
        # Clear existing handlers
        self.logger.handlers.clear()

        # Set log level
        self.logger.setLevel(getattr(logging, settings.log_level))

        # Create log directory if it doesn't exist
        settings.create_log_directory()

        # Console handler with Rich
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setLevel(getattr(logging, settings.log_level))

        # File handler
        file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Log everything to file

        # File formatter (detailed)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)

    def success(self, message: str) -> None:
        """Log success message with green color."""
        console.print(f"✓ {message}", style="success")
        self.logger.info(f"SUCCESS: {message}")

    def exception(self, message: str, exc_info: bool = True) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, exc_info=exc_info)

    def print_header(self, title: str, width: int = 70) -> None:
        """Print a formatted header."""
        console.rule(f"[bold cyan]{title}[/bold cyan]", style="cyan")
        self.logger.info(f"{'='*width}")
        self.logger.info(f"  {title}")
        self.logger.info(f"{'='*width}")

    def print_footer(self, width: int = 70) -> None:
        """Print a formatted footer."""
        console.rule(style="cyan")
        self.logger.info(f"{'='*width}")

    def print_table_row(self, label: str, value: any, style: str = "cyan") -> None:
        """Print a table-style row."""
        console.print(f"  [bold]{label:.<30}[/bold] [{style}]{value}[/{style}]")

    def print_summary(self, title: str, data: dict, success: bool = True) -> None:
        """Print a summary table."""
        self.print_header(title)

        for key, val in data.items():
            style = "success" if success else "error"
            value = val  

            if isinstance(val, bool):
                style = "success" if val else "error"
                value = "✓ Yes" if val else "✗ No"
            elif key.lower().find("error") != -1 or key.lower().find("fail") != -1:
                style = "error" if val > 0 else "success"

            self.print_table_row(key, value, style)

        self.print_footer()
logger = Logger()


def get_logger(name: str | None = None) -> Logger:
    """Get logger instance with optional name."""
    if name:
        return Logger(name)
    return logger
