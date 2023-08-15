import tarfile
from pathlib import Path


class DockerImagePackager:
    """The class to ackage image files into a tar file

    Args:
        name (str): The name of the image.
        tag (str): The tag of the image.

    Examples:
        >>> packager = ImagePackager("hello-world", "latest")
        >>> packager.package()
    """

    def __init__(self, name: str, tag: str):
        self.name = name
        self.tag = tag

    def package(self):
        """Package image files into a tar file


        Raises:
            FileNotFoundError: The specified image directory does not exist.

        Notes:
            The image files are located in the directory.
        """
        target_dirpath = Path(f"./{self.name}-{self.tag}")
        if not target_dirpath.exists():
            raise FileNotFoundError(
                f"The directory {target_dirpath} does not exist."
            )
        target_filepathes = list(target_dirpath.glob("*"))
        package_filepath = Path(f"./{self.name}-{self.tag}.tar")
        with tarfile.open(package_filepath, mode="w") as fout:
            for target_filepath in target_filepathes:
                fout.add(
                    target_filepath,
                    arcname=target_filepath.name,
                    recursive=True,
                )


if __name__ == "__main__":
    name = "hello-world"
    tag = "latest"
    packager = DockerImagePackager(name, tag)
    packager.package()
