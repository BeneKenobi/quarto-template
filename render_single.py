import shutil
import subprocess
import sys
from pathlib import Path


def comment_sidebar(lines: list[str]) -> list[str]:
    commented_lines = []
    in_sidebar = False
    sidebar_indent = 0

    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith("sidebar:"):
            in_sidebar = True
            sidebar_indent = len(line) - len(stripped_line)
            commented_lines.append(f"# {line}")
        elif in_sidebar:
            current_indent = len(line) - len(stripped_line)
            if current_indent > sidebar_indent:
                commented_lines.append(f"# {line}")
            else:
                in_sidebar = False
                commented_lines.append(line)
        else:
            commented_lines.append(line)

    return commented_lines


def process_yaml(yaml_path: Path) -> None:
    with open(yaml_path, "r") as file:
        lines = file.readlines()

    processed_lines = comment_sidebar(lines)

    with open(yaml_path, "w") as file:
        file.writelines(processed_lines)


def revert_yaml(yaml_path: Path, backup_path: Path) -> None:
    shutil.copy(backup_path, yaml_path)
    backup_path.unlink()


def main(quarto_file: str) -> None:
    yaml_path = Path("_quarto.yml")
    backup_path = yaml_path.with_suffix(".bak")

    # Create a backup
    shutil.copy(yaml_path, backup_path)

    try:
        # Process the YAML file
        process_yaml(yaml_path)

        # Run the quarto render command
        subprocess.run(["quarto", "render", quarto_file], check=True)
    finally:
        # Revert the YAML file to its original state
        revert_yaml(yaml_path, backup_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python render_single.py <quarto_file>")
        sys.exit(1)
    main(sys.argv[1])
