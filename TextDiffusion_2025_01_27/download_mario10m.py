from __future__ import annotations
import click
from pathlib import Path
import subprocess
import tqdm

@click.group()
def cli():
    pass

@cli.command()
@click.option("--output_dir", "-o", type=click.Path(exists=False))
@click.option("--ignore_files", "-i", type=str, multiple=True, default=["89.tar.gz"])
@click.option("--start", "-s", type=int, default=0)
@click.option("--end", "-e", type=int, default=500)
@click.option("--overwrite", "-f", is_flag=True)
@click.option("--require_empty_folder", "-r", is_flag=True)
def download(output_dir: str, ignore_files: str, start: int, end: int, overwrite: bool, require_empty_folder: bool):
    """
    Script to download the Mario 10M dataset, based on: https://huggingface.co/datasets/JingyeChen22/TextDiffuser-MARIO-10M
    (which gives us some instructions to do the download).

    NOTE: that in the HF repo you can see that 89.tar.gz is "unsafe". That is why we do not download it. It's not seemingly possible
    to untar it so maybe it's just corrupted in some inoccuous way but generally we avoid it anyways.
    """
    print(f"There are around {end-start} files we will download; each could be up to 3GB. That means you NEED at least 1.5TB of space (start={start}, end={end}).")
    click.confirm("Continue?", abort=True)

    # XXX when decompressed these are going to take up around 100GB because each file might have 100, 1GB examples in it, which is rather brutal, ngl

    print("Ignoring the following files: ")
    print(' - ' + '\n - '.join(ignore_files))
    click.confirm("Continue?", abort=True)
    
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        if len(list(output_dir.iterdir())) > 0 and require_empty_folder:
            print(f"Output directory {output_dir} already exists and is not empty. Exiting.")
            return
    
    assert 0 <= start < end <= 500
    
    for i in tqdm.trange(start, end + 1, 1):  # 0 to 500 inclusive
        if f"{i}.tar.gz" in ignore_files: # NOTE: later we might be able to want to do matches or something along those lines...
            print(f"Skipping {i}.tar.gz as it's in ignore list")
            continue
        
        try:
            url = f"https://huggingface.co/datasets/JingyeChen22/TextDiffuser-MARIO-10M/resolve/main/{i}.tar.gz?download=true"
            output_path = output_dir / f"{i}.tar.gz"
            if output_path.exists() and not overwrite:
                print(f"Skipping {i}.tar.gz as it already exists")
                continue
            elif output_path.exists() and overwrite:
                print(f"Overwriting {i}.tar.gz as it already exists")
                output_path.unlink()
            # print(f"Downloading {i}.tar.gz...") # Use this for debugging
            # NOTE: in my experience it's faster to use cli tools
            result = subprocess.run(["wget", "-O", output_path, url], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error (return code {result.returncode}) downloading {i}.tar.gz: {result.stderr}")
                continue
        except Exception as e:
            print(f"Error (exception thrown) downloading {i}.tar.gz: {e}")
            continue

if __name__ == "__main__":
    cli()