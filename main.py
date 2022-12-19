from src import refining, material, api
import os


if __name__ == '__main__':
    try:
        os.makedirs('./db/refining', exist_ok=True)
        os.makedirs('./db/material', exist_ok=True)
    except FileExistsError as e:
        print('error')
        pass

    api.members_to_dataframe()
    api.get_material_price()

    weaponStepMaterial = material.data_group('weapon', 1302, 1340, 1390, 1525)
    material.to_csv(weaponStepMaterial)
    # material.to_yml(material)
    armorStepMaterial = material.data_group('armor', 1302, 1340, 1390, 1525)
    material.to_csv(armorStepMaterial)
    # material.to_yml(material)

    refining.data_group(100, 60, 45, 30, 15, 10, 5, 4, 3, 1.5, 1, 0.5)
    refining.calc_avg_num()
    refining.calcStepPrice()
