import yaml
config = yaml.load(open("conf.yaml"), Loader=yaml.Loader)
log_level = config["log_level"]
