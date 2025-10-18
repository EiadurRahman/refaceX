# IMPORTS
import os, base64
import requests
# Removed tqdm import as we will use rich.progress

# Import the necessary components from rich
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn, SpinnerColumn
from rich.layout import Layout
from rich import box

# Initialize the rich console for better output
console = Console()

# CONFIGS FOR DOWNLOADER
download_path = "./downloads"

# SETUPS
if not os.path.exists(download_path):
    # Use a clean rich print for setup with a Panel for emphasis
    console.print(
        Panel(
            Text(f"Creating download directory at [bold]{download_path}[/bold]...", style="italic cyan"),
            title="[bold blue]SETUP[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
    )
    os.mkdir(download_path) # Ensure download directory exists
    console.print() # Add a small spacer after setup

# Define a custom progress display for downloads
download_progress = Progress(
    SpinnerColumn(spinner_name="dots"),
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
    auto_refresh=True,
    transient=False, # Keep the progress bar on screen after completion
)


def encode_base64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()

def decode_base64(b64_string: str) -> str:
    return base64.b64decode(b64_string.encode()).decode()

def downloader(url):
    """Downloads a file from a given URL with a rich progress bar."""
    
    # 1. Prepare Paths
    filename_base = os.path.basename(url)
    filename_full_path = os.path.join(download_path, filename_base)

    if os.path.exists(filename_full_path):
        console.print(
            Text(f"[bold yellow]{filename_base}[/bold yellow] already exists. Skipping download.", style="italic"),
            highlight=True,
        )
        console.print("-" * 50, style="dim") # Separator
        return
    
    # 2. Initial Status
    console.print(
        Text(f"🚀 Initiating download for [bold underline magenta]{filename_base}[/bold underline magenta]...", style="italic dim")
    )
    
    # 3. Request
    try:
        # Use rich's Progress context manager for the download
        with download_progress:
            # Create a new task for this download
            task = download_progress.add_task(
                "download", 
                filename=filename_base, 
                total=None
            )
            
            # Request setup
            response = requests.get(url, stream=True, timeout=30)
            
            # 4. Check Response Status
            if response.status_code == 200:
                total_file_size = int(response.headers.get('content-length', 0))
                
                # Update task total if content-length is available
                if total_file_size:
                    download_progress.update(task, total=total_file_size)
                
                # 5. Download with Rich Progress
                with open(filename_full_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            download_progress.update(task, advance=len(chunk))
                
                # Mark as finished
                download_progress.update(task, description=f"[bold green]Complete[/bold green]: [bold]{filename_base}[/bold]", completed=total_file_size)
                
                # 6. Success Output (Clean, framed look)
                console.print(
                    Panel(
                        Text(f"✅ Downloaded successfully: [bold underline]{filename_base}[/bold underline]", style="bold green"),
                        title="[bold green]STATUS[/bold green]",
                        border_style="green",
                        padding=(1, 2),
                        box=box.HEAVY
                    )
                )
                
            else:
                # 7. Failure Output (Structured, high-contrast Panel)
                download_progress.stop_task(task) # Stop the progress for this task
                console.print(
                    Panel(
                        Text(f"❌ Failed to download [bold red]{filename_base}[/bold red]. Status code: [yellow]{response.status_code}[/yellow]", style="white"),
                        title=f"[bold red]ERROR: {response.status_code}[/bold red]",
                        border_style="red",
                        box=box.DOUBLE,
                        padding=(1, 2)
                    )
                )
                
    except requests.exceptions.RequestException as e:
        # 8. Network Failure Output
        # If the context manager wasn't entered or failed early, this may not have a task to stop, 
        # but the try/except around the response request is necessary.
        try:
            download_progress.stop_task(task)
        except UnboundLocalError: # Happens if the error occurs before `task` is defined
            pass
            
        console.print(
            Panel(
                Text(f"🌐 Network Error for [bold red]{filename_base}[/bold red]: {e}", style="white"),
                title="[bold red]NETWORK FAILURE[/bold red]",
                border_style="red",
                box=box.SQUARE,
                padding=(1, 2)
            )
        )
    
    # Add a horizontal separator after each download attempt
    console.print("-" * 50, style="dim")


def download_model():
    """Defines and iterates through the list of URLs to download."""
    list_of_urls = [
        "aHR0cHM6Ly9odWdnaW5nZmFjZS5jby9QYXRpbC9pbnN3YXBwZXIvcmVzb2x2ZS9tYWluL3NpbXN3YXBfNTEyX3Vub2ZmaWNpYWwub25ueA==",
        "aHR0cHM6Ly9odWdnaW5nZmFjZS5jby90aGViaWdsYXNrb3dza2kvaW5zd2FwcGVyXzEyOC5vbm54L3Jlc29sdmUvbWFpbi9pbnN3YXBwZXJfMTI4Lm9ubng="
    ]
    
    # Use a prominent, expanded Panel for the process start
    console.print(
        Panel(
            "[b]Model Download Process[/b]", 
            style="bold magenta", 
            title_align="left", 
            border_style="magenta", 
            expand=True,
            subtitle=f"Total files: [bold]{len(list_of_urls)}[/bold]"
        )
    )
    
    # Use Layout (optional but a richer concept) to organize main steps if needed, 
    # but for sequential output, a simple loop is best.
    
    for url in list_of_urls:
        url = decode_base64(url)
        downloader(url)

    # Final summary/completion message
    console.print(
        Panel(
            Text("✨ All download attempts complete. Check the 'downloads' folder.", style="bold yellow"),
            title="[bold blue]PROCESS END[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
    )

if __name__ == "__main__":
    download_model()