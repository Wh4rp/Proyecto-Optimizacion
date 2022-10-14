from gurobipy import Model, GRB, quicksum
from data_loader import load_data
from math import ceil

if __name__ == '__main__':
    df_fs, df_foods, df_schools = load_data(
        'feeding_schedule.csv', 'foods.csv', 'schools.csv')

    # Creamos un numero arbitrariamente grande
    INF = 100000000000000000000000000000000000000000000000000000000000000000000

    # Definicion de los conjuntos

    T = range(0, 32)  # Dias del mes
    C = range(1, len(df_schools)+1)  # Colegios
    A = range(1, len(df_foods['ALIMENTO'])+1)  # Alimentos

    # Definicion de los parametros

    # Dias de caducidad
    c_a = {a: df_foods.loc[a-1, 'DIAS CADUCIDAD'] for a in A}

    # Volumen de cada alimento
    v_a = {a: df_foods.loc[a-1, 'VOLUMEN'] for a in A}

    # Volumen máximo que se puede trasladar desde CA en cm3
    V_max = 1500000000000000000

    # Volumen mínimo que se puede trasladar desde CA en cm3
    V_min = 0

    # Peso máximo que puede llevar un camión en gramos
    P_max = 2500000000000000000

    # Densidad de cada alimento "a"
    d_a = {a: df_foods.loc[a-1, 'DENSIDAD'] for a in A}

    # Tiempo mínimo entre pedidos del colegio "c" al CA
    t_min = {c: df_schools.loc[c-1, 'TIEMPO MINIMO'] for c in C}

    # Cantidad de alumnos en el colegio "c"
    n_c = {c: df_schools.loc[c-1, 'ALUMNADO'] for c in C}

    # Volumen maximo de almacenaje en el colegio "c"
    V_max_c = {c: df_schools.loc[c-1, 'VOLUMEN MAXIMO'] for c in C}

    # Volumen de alimento "a" consumido por el colegio "c" en
    # el día "t"
    v_a_c_t = {(a, c, t): n_c[c] * v_a[a] * df_fs.loc[t, df_foods.loc[a-1, 'ALIMENTO']]
               for a in A for c in C for t in T if t > 0}

    # v_a_c_t = {(a, c, t): 10 for a in A for c in C for t in T if t > 0}

    for key in v_a_c_t:
        with open('consumo.txt', 'a') as f:
            f.write(f"{key}: {v_a_c_t[key]}\n")

    # Creacion del modelo
    model = Model()

    # Definicion de las variables de decision

    # Variable 1
    X_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='X_a_c_t')

    # Variable 3
    Y_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='Y_a_c_t')

    # Variable 4
    Z_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='Z_a_c_t')

    # Funcion objetivo
    model.setObjective(
        quicksum(Y_a_c_t[a, c, t] for a in A for c in C for t in T if t > 0),
        GRB.MINIMIZE)

    # Definicion de restricciones

    # Restriccion 1
    model.addConstrs(
        (Z_a_c_t[a, c, 0] == 0 for a in A for c in C),
        name='r1')

    # Restriccion 2
    model.addConstrs(
        (Z_a_c_t[a, c, t] == X_a_c_t[a, c, t] - ceil(v_a_c_t[a, c, t])
            for a in A for c in C for t in T if t > 0),
        name='r2')

    # Restriccion 11
    model.addConstrs(
        (X_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T),
        name='r11')

    # Restriccion 12
    model.addConstrs(
        (Y_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T),
        name='r12')

    # Restriccion 13
    model.addConstrs(
        (Z_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T),
        name='r13')

    # Optimizamos
    model.optimize()

    # Imprimimos la solucion
    if model.status == GRB.Status.OPTIMAL:
        print('Obj: %g' % model.objVal)
        for v in model.getVars():
            if v.x >= 0:
                with open('solution.txt', 'a') as f:
                    f.write('%s %g\n' % (v.varName, v.x))
