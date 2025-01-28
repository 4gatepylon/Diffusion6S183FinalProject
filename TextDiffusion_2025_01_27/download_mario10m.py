from __future__ import annotations
import click
import time
from pathlib import Path
import subprocess
from multiprocessing import Pool as mp_Pool, Manager as mp_Manager
import tqdm

"""
This scripts provides functionality to download, decompress, and generally prepare the MARIO 10M dataset.

The MARIO-10M dataset can take up to 10TB of space (roughly) when fully decompressed and 1.5TB when decompressed,
so this provides the option to use smaller subsets of that dataset.

TODO(Adriano) add the option to parallelize downloads for better time performance.
TODO(Adriano) in the future we should re-release this dataset so that it can be used with huggingface datasets
more easily and we should ALSO see if there is a better way for us to compress it.
"""

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

@cli.command()
@click.option("--input_dir", "-i", type=click.Path(exists=True))
def clean(input_dir: str):
    """Delete all empty files in the input directory."""
    input_dir = Path(input_dir)
    if not input_dir.exists():
        print(f"Input directory {input_dir} does not exist. Exiting.")
        return
        
    deleted = 0
    for file_path in input_dir.iterdir():
        if file_path.is_file() and file_path.stat().st_size == 0:
            print(f"Deleting empty file: {file_path}")
            file_path.unlink()
            deleted += 1
            
    print(f"Deleted {deleted} empty files")


@cli.command()
# TODO(Adriano) improve this function to only provide all the necessary functionality and nothing else
@click.option("--input_dir", "-i", type=click.Path(exists=True))
@click.option("--output_dir", "-o", type=click.Path(exists=False), default="mnt") # NOTE: not used right now.
@click.option("--overwrite", "-f", is_flag=True)
@click.option("--require_empty_folder", "-r", is_flag=True)
@click.option("--num_workers", "-n_workers", "-n", type=int, default=1)
def decompress_outer(input_dir: str, output_dir: str, overwrite: bool, require_empty_folder: bool, num_workers: int):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    if not input_dir.exists():
        print(f"Input directory {input_dir} does not exist. Exiting.")
        return
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    elif len(list(output_dir.iterdir())) > 0 and require_empty_folder:
        print(f"Output directory {output_dir} already exists and is not empty. Exiting.")
        return
    
    tar_gzs = list(input_dir.iterdir())
    # TODO(Adriano) wtf
    # tar_gz_non_files = [tgz for tgz in tar_gzs if not tgz.is_file()]
    # assert len(tar_gz_non_files) == 0, f"Found {len(tar_gz_non_files)} non-files in {input_dir}\n{tar_gz_non_files}"
    print(f"Will decompress {len(tar_gzs)} files")
    click.confirm("Continue?", abort=True)

    if num_workers != 1:
        raise NotImplementedError("Parallel decompression not implemented yet")
    
    for input_path in tqdm.tqdm(tar_gzs):
        if not input_path.name.endswith(".tar.gz"):
            print(f"Skipping {input_path} as it's not a .tar.gz file")
            continue
        try:
            result = subprocess.run(["tar", "-xzf", input_path.as_posix()], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error (return code {result.returncode}) decompressing {input_path}: {result.stderr}")
                continue
        except Exception as e:
            print(f"Error (exception thrown) decompressing {input_path}: {e}")
            continue

# XXX(Adriano) is this locking going to lead to high overhead?
def __helper_decompress_worker(args):
    file_path, counter_tried, counter_processed, lock = args
    result = subprocess.run(["tar", "-xzf", file_path.name, "--overwrite"], cwd=file_path.parent.as_posix(), capture_output=True, text=True)
    with lock:
        counter_tried.value += 1
        if result.returncode == 0:
            counter_processed.value += 1
    

@cli.command()
@click.option("--input_path", "-i", type=click.Path(exists=True))
# NOTE: I did some testing and 32 seemed fastest for some echo commands so yolo.
@click.option("--num_workers", "-n_workers", "-n", type=int, default=32)
def decompress_inner(input_path: Path, num_workers: int):
    """
    Decompress the inner .tar.gz fils per: https://huggingface.co/datasets/JingyeChen22/TextDiffuser-MARIO-10M
    NOTE: This can lead to a large expansion of the space taken which could be pretty brutal if you have a small hard-drive.

    As said above you should have 10-20TB total.

    In expectation I would say this will be an up to 2x explosion in space (3x including the original .tar.gz files).

    This can be really SLOW FYI.
    """
    
    mnt_path = Path(input_path) / "mnt/localdata4/users/jingyechen/further"
    assert mnt_path.exists(), f"Expected {mnt_path} to exist"
    # print(mnt_path.as_posix()) # DEBUG

    tar_gzs = list(mnt_path.glob("**/*.tar.gz"))
    assert len(tar_gzs) > 0, f"Expected 500 .tar.gz files, got {len(tar_gzs)}"
    sizes_gb = [file_path.stat().st_size / (1024 ** 3) for file_path in tar_gzs]
    total_size_gb = sum(sizes_gb)
    print(f"Will decompress {len(tar_gzs)} files. Total size BEFORE compression: {total_size_gb:.2f} GB (expect 2x more ADDED so -> {total_size_gb * 3:.2f} GB)")
    click.confirm(f"Continue?", abort=True)

    time_start = time.time()
    if num_workers == 1:
        print("Decompressing in single-threaded mode; are you sure you want this?")
        click.confirm("Continue?", abort=True)
        num_decompressed = 0
        for file_path in tqdm.tqdm(tar_gzs):
            try:
                result = subprocess.run(["tar", "-xzf", file_path.name, "--overwrite"], cwd=file_path.parent.as_posix(), capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error (return code {result.returncode}) decompressing {file_path}: {result.stderr}")
                    continue
                # print(f"Decompressed {file_path.as_posix()}") # DEBUG
                num_decompressed += 1
            except Exception as e:
                print(f"Error (exception thrown) decompressing {file_path}: {e}")
                continue
        print(f"Decompressed {num_decompressed} files in {time.time() - time_start:.2f} seconds")
        return
    else:
        print(f"Decompressing in parallel mode with {num_workers} workers")
        click.confirm("Continue?", abort=True)

        with mp_Manager() as manager:
            counter_tried = manager.Value('i', 0)
            counter_processed = manager.Value('i', 0)
            lock = manager.Lock()
            with mp_Pool(num_workers) as pool:
                # Create progress bar
                pbar = tqdm.tqdm(total=len(tar_gzs), desc='Processing')
                args = [(file_path, counter_tried, counter_processed, lock) for file_path in tar_gzs]

                # Run asynchronously to be able to update a pbar using tqdm
                async_result = pool.map_async(__helper_decompress_worker, args)
                while not async_result.ready():
                    # Update progress bar to match the counter
                    pbar.n = counter_tried.value
                    pbar.refresh()
                    time.sleep(0.1)

        print(f"Decompressed {(counter_processed.value / counter_tried.value if counter_tried.value > 0 else 0):.2f} of files: {counter_processed.value} (tried {counter_tried.value}) files in {time.time() - time_start:.2f} seconds")

def __helper_is_valid_entry_parent_path(parent_path: Path):
    has_image = (parent_path / "image.png").exists() or (parent_path / "image.jpg").exists()
    has_caption = (parent_path / "caption.txt").exists()
    has_info = (parent_path / "info.json").exists()
    has_charseg = (parent_path / "charseg.npy").exists()
    has_ocr = (parent_path / "ocr.txt").exists()
    return has_image and has_caption and has_info and has_charseg and has_ocr

@cli.command()
@click.option("--input_path", "-i", type=click.Path(exists=True), default=None)
def final_info(input_path: Path):
    """Just print out how many entries (i.e. images with information about their text) there are."""
    if input_path is None:
        input_path = Path.cwd()
    image_paths = list(input_path.glob("**/caption.txt"))
    parent_paths = list(set([image_path.parent for image_path in tqdm.tqdm(image_paths, desc="Getting parent paths")]))
    valid_parent_paths = [parent_path for parent_path in tqdm.tqdm(parent_paths, desc="Checking entries") if __helper_is_valid_entry_parent_path(parent_path)]
    print(f"There are {len(valid_parent_paths)} entries (out of total {len(parent_paths)} entries) in {input_path}")

if __name__ == "__main__":
    cli()