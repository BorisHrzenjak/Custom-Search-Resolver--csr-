"""
Command-line interface for CSR tool
"""
import os
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from pathlib import Path
from datetime import datetime
import re
import glob

console = Console()

def format_size(size_bytes):
    """Convert size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"

def search_files(name=None, content=None, file_type=None, size=None, modified=None, 
                path=None, recursive=False, syswide=False, output_format="table"):
    """Search for files based on given criteria"""
    if syswide:
        if os.name == 'nt':  # Windows
            drives = [d + ':/' for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(d + ':/')]
        else:  # Unix-like systems
            drives = ['/']
        recursive = True
    else:
        drives = [path or os.getcwd()]

    # Process size filter
    size_op = None
    size_value = None
    if size:
        match = re.match(r"([<>])([\d.]+)(MB|GB|KB|B)", size)
        if match:
            op, val, unit = match.groups()
            multiplier = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            size_op = op
            size_value = float(val) * multiplier[unit]

    results = []
    pattern = "**/*" if recursive else "*"
    
    try:
        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # Create the main progress task
            search_task = progress.add_task("[cyan]Searching files...", total=None)
            
            for drive in drives:
                try:
                    base_path = Path(drive)
                    # Update progress description
                    progress.update(search_task, description=f"[cyan]Searching in {drive}...")
                    
                    file_list = list(base_path.rglob("*") if recursive else base_path.glob("*"))
                    progress.update(search_task, total=len(file_list))
                    
                    for i, file_path in enumerate(file_list):
                        try:
                            if not file_path.is_file():
                                continue

                            # Update progress
                            progress.update(search_task, completed=i+1, 
                                         description=f"[cyan]Processing: {file_path.name}")

                            # Skip system directories when doing system-wide search
                            if syswide:
                                skip_dirs = ['Windows', 'Program Files', 'Program Files (x86)', 
                                           '$Recycle.Bin', 'System Volume Information']
                                if any(sd in str(file_path) for sd in skip_dirs):
                                    continue
                            
                            # Apply filters
                            if name and not file_path.match(name):
                                continue
                                
                            if file_type and not str(file_path).lower().endswith(file_type.lower()):
                                continue
                                
                            file_stat = file_path.stat()
                            
                            if size_value:
                                file_size = file_stat.st_size
                                if size_op == '>' and not file_size > size_value:
                                    continue
                                if size_op == '<' and not file_size < size_value:
                                    continue
                            
                            if content:
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        if not re.search(content, f.read()):
                                            continue
                                except (UnicodeDecodeError, PermissionError):
                                    continue
                            
                            results.append({
                                'path': str(file_path),
                                'size': file_stat.st_size,
                                'modified': datetime.fromtimestamp(file_stat.st_mtime)
                            })
                            
                        except Exception as e:
                            console.print(f"[red]Error processing file {file_path}: {str(e)}[/red]")
                            
                except Exception as e:
                    console.print(f"[red]Error searching drive {drive}: {str(e)}[/red]")
                    
    except PermissionError as e:
        console.print(f"[red]Permission denied: {e}[/red]")
    
    return results

@click.command()
@click.option('--name', help='Search for files by name (supports wildcards)')
@click.option('--content', help='Search for files containing specific text')
@click.option('--type', 'file_type', help='Search for files by type (extension)')
@click.option('--size', help='Search for files by size (e.g., >10MB, <1GB)')
@click.option('--modified', help='Search for files by last modified date')
@click.option('--path', type=click.Path(exists=True), help='Directory to search within')
@click.option('--recursive/--no-recursive', default=False, help='Search recursively')
@click.option('--syswide/--local', default=False, help='Search system-wide (on whole PC) or local directory')
@click.option('--output', type=click.Choice(['table', 'list', 'json']), default='table',
              help='Output format')
def main(name, content, file_type, size, modified, path, recursive, syswide, output):
    """
    CSR - Command-Line Search and Replace tool
    
    Search for files and content within files using various criteria.
    
    Options:
      --name TEXT          Search for files by name (supports wildcards)
      --content TEXT       Search for files containing specific text
      --type TEXT         Search for files by type (extension)
      --size TEXT         Search for files by size (e.g., >10MB, <1GB)
      --modified TEXT     Search for files by last modified date
      --syswide/--local  Search system-wide (on whole PC) or local directory
      --path PATH         Directory to search within
      --recursive        Search recursively in subdirectories
      --output [table|list|json]  Output format (default: table)
    """
    try:
        results = search_files(name, content, file_type, size, modified, 
                             path, recursive, syswide, output)
        
        if not results:
            console.print("[yellow]No files found matching the criteria.[/yellow]")
            return
        
        if output == 'table':
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Path")
            table.add_column("Size")
            table.add_column("Modified")
            
            for result in results:
                table.add_row(
                    result['path'],
                    format_size(result['size']),
                    result['modified'].strftime('%Y-%m-%d %H:%M:%S')
                )
            console.print(table)
            
        elif output == 'list':
            for result in results:
                console.print(result['path'])
                
        else:  # json
            import json
            json_results = [{
                'path': r['path'],
                'size': r['size'],
                'modified': r['modified'].isoformat()
            } for r in results]
            console.print(json.dumps(json_results, indent=2))
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == '__main__':
    main()
