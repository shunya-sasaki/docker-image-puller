import argparse
from imagepuller.puller import DockerImagePuller
from imagepuller.packager import DockerImagePackager

parser = argparse.ArgumentParser(
    description="Pull docker image with out Docker"
)
parser.add_argument("--image", "-i", help="Image name to pull")
parser.add_argument("--tag", "-t", help="Image tag to pull")
parser.add_argument(
    "--architecture", "-a", help="Architecture to pull", default="amd64"
)
parser.add_argument("--variant", "-v", help="Variant to pull", default="")
parser.add_argument(
    "--proxy", "-p", help="Proxy to use", default=None, type=str
)
parser.add_argument(
    "--encoding", "-e", help="Encoding to use", default="utf-8", type=str
)


def run(
    name: str = None,
    tag: str = None,
    architecture: str = None,
    variant: str = None,
    proxy: str | None = None,
    encoding: str = "utf-8",
):
    args = parser.parse_args()
    if name is None:
        name = args.image
    if tag is None:
        tag = args.tag
    if architecture is None:
        architecture = args.architecture
    if variant is None:
        variant = args.variant
    if proxy is None:
        proxy = args.proxy
    if encoding == "utf-8":
        encoding = args.encoding
    puller = DockerImagePuller(
        name=name,
        tag=tag,
        target_architecture=architecture,
        target_variant=variant,
    )
    puller.pull_image()
    packager = DockerImagePackager(name=name, tag=tag)
    packager.package()
