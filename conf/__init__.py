import yaml
import pathlib

path = pathlib.Path(__file__).parent / "conf.yml"
with path.open(mode="rb") as yamlfile:
    conf = yaml.load(yamlfile, Loader=yaml.FullLoader)
