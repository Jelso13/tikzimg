import argparse
import logging
import os
import subprocess
from pathlib import Path
import tempfile
from typing import Optional
import shutil

from .utils import get_default_editor


def run_command(command: list[str], cwd: Path) -> None:
    # ... (code for run_command is identical to the original script) ...
    logging.info(f"Running command: `{' '.join(command)}` in `{cwd}`")
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if process.stdout:
            logging.debug(f"STDOUT: {process.stdout}")
        if process.stderr:
            logging.warning(f"STDERR: {process.stderr}")
    except FileNotFoundError:
        logging.error(
            f"Command not found: `{command[0]}`. Is it in your system's PATH?"
        )
        raise
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Command `{' '.join(command)}` failed with exit code {e.returncode}."
        )
        logging.error(f"STDOUT: {e.stdout}")
        logging.error(f"STDERR: {e.stderr}")
        raise


def get_file_content(f: Path) -> str:
    """
    If no file is specified as the input, use the template, otherwise use the specified file.
    Return the contents of the chosen file.
    """
    try:
        if not f:
            raise FileNotFoundError(
                f"Error: The target file {f} does not exist"
            )
        return f.read_text(encoding="utf-8")
    except Exception as e:
        print(f"An error occurred while reading {e}")
        raise


def compile_tempfile(source_tex_path: Path) -> None:
    """
    Compiles a tex file
    """
    if not source_tex_path.is_file():
        raise FileNotFoundError(f"file not found at: {source_tex_path}")

    temp_dir = source_tex_path.parent
    base_name = source_tex_path.stem  # filename without the extension

    logging.info(f"Starting compilation for '{source_tex_path}'...")
    try:
        process = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-jobname={base_name}",
                str(source_tex_path),
            ],
            cwd=temp_dir,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if process.stdout:
            logging.debug(f"STDOUT: {process.stdout.strip()}")
        if process.stderr:
            logging.warning(f"STDERR: {process.stderr.strip()}")
    except FileNotFoundError:
        logging.error(f"command not found")
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}.")
        logging.error(f"Captured STDOUT:\n{e.stdout}")
        logging.error(f"Captured STDERR:\n{e.stderr}")


def convert_filetype(latex_file: Path, filetype: str) -> Optional[str]:
    """
    Function that takes the location of a latex file, finds its output and converts to the desired filetype.
    """
    # dvisvgm -P e.pdf -o out.svg
    temp_dir = latex_file.parent
    base_name = latex_file.stem  # filename without the extension

    output_file = f"{temp_dir}/{base_name}.{filetype}"

    if filetype == "svg":
        try:
            process = subprocess.run(
                ["dvisvgm", "-P", f"{temp_dir}/{base_name}.pdf", "-o", output_file],
                cwd=temp_dir,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            return output_file
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed with exit code {e.returncode}.")
            logging.error(f"Captured STDOUT:\n{e.stdout}")
            logging.error(f"Captured STDERR:\n{e.stderr}")
    else:
        logging.error(f"filetype '{filetype}' is not currently supported:")
    return None

def copy_to_output(latex_file: Path, output_file: Path, output_location: Path) -> None:
    """
    Function that takes the output locations and copies them to the output location
    """
    temp_dir = latex_file.parent
    base_name = latex_file.stem  # filename without the extension

    # If the output_location is a file, then move the converted output to the output location

    # Otherwise, copy the converted output to the output_location/{base_name}.ext
    
    output_basename = output_location.stem
    if os.path.isdir(output_location):
        output_directory = output_location
        output_basename = base_name
    else:
        output_directory = output_location.parent

    logging.info(f"{latex_file=}")
    logging.info(f"{output_file=}")
    logging.info(f"{output_location=}")
    logging.info(f"{output_directory=}")
    logging.info(f"{output_basename=}")

    try:
        output_directory.mkdir(parents=True, exist_ok=True)

        source_output_location = (output_directory / output_basename).with_suffix(".tex")
        product_output_location = (output_directory / output_basename).with_suffix(output_file.suffix)
        logging.info(f"Attempting to copy {latex_file} to {source_output_location}")
        shutil.copy(latex_file, source_output_location)
        logging.info(f"Attempting to copy {output_file} to {product_output_location}")
        shutil.copy(output_file, product_output_location)
    except Exception as e:
        logging.error(f"failed to copy files to output directory {e}")
        raise


def process_command(args: argparse.Namespace) -> None:
    editor = get_default_editor()
    logging.info(
        f"Opening with editor: `{editor}`. Close the editor to continue..."
    )
    # run_command([editor, "a.tex"], cwd=Path.cwd())
    logging.info("Please save and close the editor to continue.")

    # Create a temporary directory with which to create and compile the files
    with tempfile.TemporaryDirectory(prefix="latex-compile-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        logging.info(f"Created temporary workspace: {temp_dir}")

        # 2. Create your source .tex file INSIDE that directory.
        source_file = temp_dir / "fig.tex"

        logging.info(f"Opening {source_file} with '{editor}'...")
        if args.file:
            logging.info(f"filling the content with {args.file}")
            content = get_file_content(args.file)
        else:
            logging.info(
                f"filling the content with {Path(__file__).resolve().parent / "TEMPLATE.tex"}"
            )
            content = get_file_content(
                Path(__file__).resolve().parent / "TEMPLATE.tex"
            )
        source_file.write_text(content, encoding="utf-8")
        logging.info(f"Source file created: {source_file}")

        subprocess.run([editor, source_file])

        compile_tempfile(source_file)

        output_file = convert_filetype(source_file, args.type)

        # copy the tex file and the svg to the output
        if output_file is not None:
            copy_to_output(source_file, Path(output_file), args.output)

    # try:
    #     # This is the key part: subprocess.run() is a blocking call.
    #     subprocess.run([editor, str(file_path)], check=True)
    # except FileNotFoundError:
    #     print(f"Error: Editor '{editor}' not found. Please check your PATH.")
    # except subprocess.CalledProcessError as e:
    #     print(f"Editor exited with an error (code {e.returncode}).")
    # finally:
    #     file_path.unlink()
