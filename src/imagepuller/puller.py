import json
from pathlib import Path

import requests


def fetch_token(name: str) -> str:
    """Get token from docker hub

    Args:
        name (str): Image name.

    Returns:
        str: Token string.
    """
    url = (
        "https://auth.docker.io/token"
        + "?service=registry.docker.io"
        + f"&scope=repository:library/{name}:pull"
    )
    ret = requests.get(url)
    ret_json = ret.json()
    token = ret_json["token"]
    return token


def fetch_manifest(
    token: str, name: str, tag: str, ouput_dir: str | Path = None
) -> json:
    """Get manifest from docker hub

    Args:
        token (str): Token string.
        name (str): Image name.
        tag (str): Image tag.
        ouput_dir (str | Path, optional): Output directory.
            Defaults to None.

    Returns:
        json: Manifest json.
    """
    if ouput_dir is not None:
        ouput_dirpath = Path(ouput_dir)
        ouput_dirpath.mkdir(exist_ok=True)
    url = f"https://registry-1.docker.io/v2/library/{name}/manifests/{tag}"
    ret = requests.get(
        url=url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": ",".join(
                [
                    "application/vnd.docker.distribution.manifest.v2+json",
                    "application/vnd.docker.distribution"
                    + ".manifest.list.v2+json",
                    "application/vnd.docker.distribution.manifest.v1+json",
                    "application/vnd.oci.image.manifest.v1+json",
                    "application/vnd.oci.image.index.v1+json",
                ]
            ),
        },
        allow_redirects=True,
    )
    ret_json = ret.json()
    if ouput_dir is not None:
        with open(ouput_dirpath.joinpath("manifest.json"), "w") as wb:
            json.dump(ret_json, wb, indent=4)
    return ret_json


def fetch_config(name: str, manifest: json, token: str):
    """Get config file from docker hub

    Args:
        name (str): Image name.
        manifest (json): Manifest json.
        token (str): Token string.
    """
    digest = manifest["config"]["digest"]
    ret = requests.get(
        url=f"https://registry-1.docker.io/v2/library/{name}/blobs/{digest}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        allow_redirects=True,
    )
    ret_json = ret.json()
    return ret_json


def fetch_sub_manifest(
    token,
    name,
    manifest: json,
    target_architecture: str = "amd64",
    target_variant: str = "",
    output_dir: str | Path = None,
):
    """Get sub manifest from docker hub

    Args:
        token (str): Token string.
        name (str): Image name.
        manifest (json): Manifest json.
        target_architecture (str, optional): Target architecture.
            Defaults to "amd64".
        target_variant (str, optional): Target variant.
            Defaults to "".
        output_dir (str | Path, optional): Output directory.
    """
    if output_dir is not None:
        output_dirpath = Path(output_dir)
    for layer in manifest["manifests"]:
        if layer["platform"]["architecture"] == target_architecture:
            if "variant" not in layer["platform"]:
                digest = layer["digest"]
                break
            elif layer["platform"]["variant"] == target_variant:
                digest = layer["digest"]
                break
            else:
                digest = layer["digest"]
    sub_manifest = requests.get(
        url="https://registry-1.docker.io/v2/library/"
        + f"{name}/manifests/{digest}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": ",".join(
                [
                    "application/vnd.docker.distribution.manifest.v2+json",
                    "application/vnd.docker.distribution."
                    + "manifest.list.v2+json",
                    "application/vnd.docker.distribution.manifest.v1+json",
                    "application/vnd.oci.image.index.v1+json",
                    "application/vnd.oci.image.manifest.v1+json",
                ]
            ),
        },
    )
    sub_manifest_json = sub_manifest.json()
    if output_dir is not None:
        with open(output_dirpath.joinpath("sub_manifest.json"), "w") as wb:
            json.dump(sub_manifest_json, wb, indent=4)
    return sub_manifest_json


def fetch_config_file(
    token, name, sub_manifest_json, output_dir: str | Path = "./"
):
    """Download config file form docker hub

    Args:
        token (str): Token string.
        name (str): Image name.
        sub_manifest_json (json): Sub manifest json.
        output_dir (str | Path, optional): Output directory.
    """
    output_dirpath = Path(output_dir)
    config_digest = sub_manifest_json["config"]["digest"]
    config_id = config_digest.replace("sha256:", "")
    config_file = output_dirpath.joinpath(f"{config_id}.json")
    header = requests.get(
        url="https://registry-1.docker.io/v2/library/"
        + f"{name}/blobs/{config_digest}",
        headers={"Authorization": f"Bearer {token}"},
    )
    config_json = header.json()
    with open(config_file, "w") as wb:
        json.dump(config_json, wb, indent=4)
    return config_json


def fetch_layer_file(
    token, name, layer_meta, config_json: json, output_dir: str
):
    """Download layer file form docker hub

    Args:
        token (str): Token string.
        name (str): Image name.
        layer_meta (json): Layer meta json.
        config_json (json): Config json.
        output_dir (str): Output directory.
    """
    output_dirpath = Path(output_dir)
    # layer_media_type = layer_meta["mediaType"]
    layer_digest = layer_meta["digest"]
    layer_id = layer_digest.replace("sha256:", "")
    output_sub_dirpath = output_dirpath.joinpath(layer_id)
    output_sub_dirpath.mkdir(exist_ok=True)
    version_filepath = output_sub_dirpath.joinpath("VERSION")
    with open(version_filepath, "w") as fout:
        fout.write("1.0\n")
    dict_json = {
        "id": layer_id,
    }
    for key in [
        "architecture",
        "config",
        "container",
        "container_config",
        "created",
        "docker_version",
        "os",
    ]:
        dict_json[key] = config_json[key]
    output_sub_dirpath.mkdir(exist_ok=True)
    with open(output_sub_dirpath.joinpath("json"), "w") as fout:
        json.dump(dict_json, fout, indent=4)
    layer_tar_filepath = output_sub_dirpath.joinpath("layer.tar")
    ret = requests.get(
        url="https://registry-1.docker.io/v2/library/"
        + f"{name}/blobs/{layer_digest}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        allow_redirects=True,
    )
    content = ret.content
    with open(layer_tar_filepath, "wb") as wb:
        wb.write(content)
    return layer_id


def export_repositories_file(name, tag, output_dir: str):
    """Export `repositories` file

    Args:
        name (str): Name of image.
        tag (str): Tag of image.
        output_dir (str): Output directory.
    """
    output_dirpath = Path(output_dir)
    dict_repository = {name: {tag: ""}}
    with open(output_dirpath.joinpath("repositories"), "w") as fout:
        json.dump(dict_repository, fout, indent=4)


def export_manifest_file(
    name, tag, sub_manifest_json, layers: list[str], output_dir: str
):
    """Export `manifest.json` file

    Args:
        name (str): Name of image.
        tag (str): Tag of image.
        sub_manifest_json (json): Sub manifest json.
        layers (list[str]): List of layer id.
    """
    output_dirpath = Path(output_dir)
    dict_manifest = [
        {
            "Config": sub_manifest_json["config"]["digest"].replace(
                "sha256:", ""
            )
            + ".json",
            "RepoTags": [f"{name}:{tag}"],
            "Layers": layers,
        }
    ]
    with open(output_dirpath.joinpath("manifest.json"), "w") as fout:
        json.dump(dict_manifest, fout, indent=4)


class DockerImagePuller:
    """Docker image puller

    Args:
        name (str): Name of image.
        tag (str): Tag of image.
        target_architecture (str, optional): Target architecture.
            Defaults to "arm64".
        target_variant (str, optional): Target variant. Defaults to "v8".
    """

    def __init__(
        self,
        name,
        tag,
        target_architecture: str = "arm64",
        target_variant: str = "v8",
    ):
        self.name = name
        self.tag = tag
        self.target_architecture = target_architecture
        self.target_variant = target_variant
        ouput_dir = f"./{name}-{tag}"
        self.output_dirpath = Path(ouput_dir)

    def pull_image(self):
        """Pull docker image from docker hub and exort to local directory"""

        self.output_dirpath.mkdir(exist_ok=True)

        token = fetch_token(name=self.name)
        manifest = fetch_manifest(
            token=token, name=self.name, tag=self.tag, ouput_dir=None
        )
        sub_manifest_json = fetch_sub_manifest(
            token,
            self.name,
            manifest,
            output_dir=None,
            target_architecture=self.target_architecture,
            target_variant=self.target_variant,
        )
        config_json = fetch_config_file(
            token, self.name, sub_manifest_json, output_dir=self.output_dirpath
        )
        layers = []
        for layer_meta in sub_manifest_json["layers"]:
            idx = fetch_layer_file(
                token,
                self.name,
                layer_meta,
                config_json,
                output_dir=self.output_dirpath,
            )
            layers.append(idx + "/layer.tar")
        export_repositories_file(
            self.name, self.tag, output_dir=self.output_dirpath
        )
        export_manifest_file(
            self.name,
            self.tag,
            sub_manifest_json,
            layers=layers,
            output_dir=self.output_dirpath,
        )
