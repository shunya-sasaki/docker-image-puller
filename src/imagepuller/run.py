import argparse
from imagepuller.puller import DockerImagePuller

parser = argparse.ArgumentParser(
    description="Pull docker image with out Docker"
)
parser.add_argument("--image", "-i", help="Image name to pull")
parser.add_argument("--tag", "-t", help="Image tag to pull")
parser.add_argument(
    "--architectures", "-a", help="Architectures to pull", default="amd64"
)
parser.add_argument("--variant", "-v", help="Variant to pull", default="")


def run(
    name: str = None,
    tag: str = None,
    architecture: str = None,
    variant: str = None,
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
    puller = DockerImagePuller(
        name=name,
        tag=tag,
        target_architecture=architecture,
        target_variant=variant,
    )
    puller.pull_image()
