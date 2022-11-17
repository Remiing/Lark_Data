from util import refining, material


if __name__ == '__main__':
    data = refining.data_group(15, 10, 5, 4, 3, 1.5, 1, 0.5)
    refining.to_csv(data)

    material = material.data_group(1302, 1340, 1390, 1525)
    material.to_yml(material)
