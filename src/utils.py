import yaml


def load_yaml(path):
    with open(path, encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


