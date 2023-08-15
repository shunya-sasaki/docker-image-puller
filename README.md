# Docker Image Puller

Pull a docker image from Docker Hub without Docker.

## Requirements

-   Python 3
    -   requests

## Setup

```shell
pip install git+https://github.com/shunya-sasaki/docker-image-puller.git
```

## Usage

### Command line

To execute form the command line, run the command as follows.

```shell
pydocker-pull -i IMAGE -t TAG -a ARCHITECTURE -v VARIANT
```

IMAGE
: Image name to pull. (e.g.: "alpine")

TAG
: Tag name to pull. (e.g.: "3.10")

ARCHITECTURE
: Architecture to pull. (e.g.: "arm64")

VARIANT
: Variant to pull. (e.g.: "v8")

### Python script

To execute from the Python script,
use `DockerImagePuller` class as follows.

```python
from imagepuller import DockerImagePuller

name = "alpine"
tag = "3.10"
architecture = "arm64"
variant = "v8"

puller = DockerImagePuller(
    name=name,
    tag=tag,
    target_architecture=architecture,
    target_variant=variant,
)
puller.pull_image()
```

## Author

Shunya Sasaki &lt;shunya.sasaki1120@gmail.com&gt;

## License

[MIT License](./LICENSE)
