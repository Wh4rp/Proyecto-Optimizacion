from gurobipy import Model, GRB, quicksum
from minuta import load_data

if __name__ == '__main__':
    df_am, df_foods = load_data('alimentation-monthly.csv', 'foods.csv')
    # print(df_am)
    print(df_foods['ALIMENTO'])

    # Definicion de los conjuntos
    T = range(1, 32) # Dias del mes
    C = range(1, 4)  # Colegios
    A = range(1, 4)  # Alimentos
