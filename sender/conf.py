import yaml
config = yaml.load(open("conf.yaml"), Loader=yaml.Loader)
token = config["token"]
check_base_rate = config["check_base_rate"]
