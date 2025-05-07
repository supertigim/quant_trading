import subprocess
import os
import argparse
from pathlib import Path


def export_requirements(env: str):
    """Export requirements for specified environment."""
    # Create requirements directory if it doesn't exist
    requirements_dir = Path("requirements")
    requirements_dir.mkdir(exist_ok=True)

    # Set output file based on environment
    output_file = requirements_dir / f"{env}.txt"

    # Base command
    cmd = [
        "poetry",
        "export",
        "--format",
        "requirements.txt",
        "--output",
        str(output_file),
        "--without-hashes",
    ]

    # Add environment-specific options
    if env == "prod":
        # Production: only main dependencies, no dev dependencies
        cmd.extend(["--without", "dev"])
    elif env == "staging":
        # Staging: include dev dependencies but exclude test dependencies
        cmd.extend(["--with", "dev", "--without", "test"])
    else:  # dev
        # Development: include all dependencies
        cmd.extend(["--with", "dev"])

    # Run the export command
    subprocess.run(cmd, check=True)
    print(f"Requirements exported to {output_file}")


def post_install():
    """Automatically update requirements.txt after poetry install or add."""
    print("Updating all requirements files after dependency changes...")
    # Update all environment requirements
    for env in ["dev", "staging", "prod"]:
        export_requirements(env)
    print("All requirements files updated successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Export requirements for different environments"
    )
    parser.add_argument(
        "environment",
        choices=["dev", "staging", "prod", "all"],
        default="dev",
        help="Environment to export requirements for (default: dev)",
    )

    args = parser.parse_args()

    if args.environment == "all":
        print("Exporting requirements for all environments...")
        for env in ["dev", "staging", "prod"]:
            export_requirements(env)
        print("All requirements files exported successfully!")
    else:
        export_requirements(args.environment)


if __name__ == "__main__":
    main()
