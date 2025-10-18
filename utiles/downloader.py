import os, base64
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import (
    Progress, BarColumn, TextColumn, TransferSpeedColumn,
    TimeRemainingColumn, SpinnerColumn
)
from rich import box

console = Console()
download_path = "./downloads"

# Setup panel
if not os.path.exists(download_path):
    console.print(
        Panel(
            Text(f"Creating download directory at [bold]{download_path}[/bold]...", style="italic cyan"),
            title="[bold blue]SETUP[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
    )
    os.mkdir(download_path)
    console.print()  # small spacer


# Clean, compact progress display
def make_progress():
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.fields[filename]}", justify="left"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True  # clears when done
    )


def encode_base64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def decode_base64(b64_string: str) -> str:
    return base64.b64decode(b64_string.encode()).decode()


def downloader(url):
    filename_base = os.path.basename(url)
    filename_full_path = os.path.join(download_path, filename_base)

    if os.path.exists(filename_full_path):
        console.print(
            Text(f"[bold yellow]{filename_base}[/bold yellow] already exists. Skipping download.", style="italic"),
            highlight=True,
        )
        console.print("-" * 50, style="dim")
        return

    # Initial status (printed cleanly before progress starts)
    console.print()
    console.print(
        f"🚀 Initiating download for [bold underline magenta]{filename_base}[/bold underline magenta]...",
        style="italic dim"
    )

    progress = make_progress()
    task_id = progress.add_task("download", filename=filename_base, total=0)

    try:
        with progress:
            response = requests.get(url, stream=True, timeout=30)

            if response.status_code == 200:
                total_file_size = int(response.headers.get('content-length', 0))
                if total_file_size:
                    progress.update(task_id, total=total_file_size)

                with open(filename_full_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task_id, advance=len(chunk))

                progress.stop_task(task_id)

                # Success panel after progress completes
                console.print(
                    Panel(
                        Text(
                            f"✅ Downloaded successfully:\n[bold underline]{filename_base}[/bold underline]",
                            style="bold green"
                        ),
                        title="[bold green]STATUS[/bold green]",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                )

            else:
                progress.stop_task(task_id)
                console.print(
                    Panel(
                        Text(
                            f"❌ Failed to download [bold red]{filename_base}[/bold red].\n"
                            f"Status code: [yellow]{response.status_code}[/yellow]",
                            style="white"
                        ),
                        title=f"[bold red]ERROR {response.status_code}[/bold red]",
                        border_style="red",
                        box=box.DOUBLE,
                        padding=(1, 2)
                    )
                )

    except requests.exceptions.RequestException as e:
        console.print(
            Panel(
                Text(f"🌐 Network Error for [bold red]{filename_base}[/bold red]:\n{e}", style="white"),
                title="[bold red]NETWORK FAILURE[/bold red]",
                border_style="red",
                box=box.SQUARE,
                padding=(1, 2)
            )
        )

    console.print("-" * 50, style="dim")


def download_model():
    list_of_urls = [
        "aHR0cHM6Ly9odWdnaW5nZmFjZS5jby9QYXRpbC9pbnN3YXBwZXIvcmVzb2x2ZS9tYWluL3NpbXN3YXBfNTEyX3Vub2ZmaWNpYWwub25ueA==",
        "aHR0cHM6Ly9odWdnaW5nZmFjZS5jby90aGViaWdsYXNrb3dza2kvaW5zd2FwcGVyXzEyOC5vbm54L3Jlc29sdmUvbWFpbi9pbnN3YXBwZXJfMTI4Lm9ubng="
    ]

    console.print()
    console.print(
        Panel(
            "[b]Model Download Process[/b]",
            style="bold magenta",
            border_style="magenta",
            expand=True,
            subtitle=f"Total files: [bold]{len(list_of_urls)}[/bold]"
        )
    )

    for url in list_of_urls:
        downloader(decode_base64(url))

    console.print()
    console.print(
        Panel(
            Text("✨ All download attempts complete.\nCheck the 'downloads' folder.", style="bold yellow"),
            title="[bold blue]PROCESS END[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
    )


if __name__ == "__main__":
    download_model()
