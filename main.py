from gurobipy import Model, GRB, quicksum
from data_loader import load_data
from math import ceil

if __name__ == '__main__':
    df_fs, df_foods, df_schools = load_data(
        'feeding_schedule.csv', 'foods.csv', 'schools.csv')

    # Creamos un numero arbitrariamente grande
    INF = 10000000000000000000000000000000000000000

    # Definicion de los conjuntos

    T = range(0, 32)  # Dias del mes
    T_V = range(0, 1005)  # Dias de caducidad
    C = range(1, len(df_schools) + 1)  # Colegios
    A = range(1, len(df_foods['ALIMENTO'])+1)  # Alimentos

    # Definicion de los parametros

    # Dias de caducidad
    c_a = {a: df_foods.loc[a-1, 'DIAS CADUCIDAD'] for a in A}

    # Volumen de cada alimento
    v_a = {a: df_foods.loc[a-1, 'VOLUMEN'] for a in A}

    # Volumen máximo que se puede trasladar desde CA en cm3
    V_max = 15000

    # Volumen mínimo que se puede trasladar desde CA en cm3
    V_min = 0

    # Peso máximo que puede llevar un camión en gramos
    P_max = 25000

    # Densidad de cada alimento "a"
    d_a = {a: df_foods.loc[a-1, 'DENSIDAD'] for a in A}

    # Tiempo mínimo entre pedidos del colegio "c" al CA
    t_min_c = {c: df_schools.loc[c-1, 'TIEMPO MINIMO'] for c in C}

    # Cantidad de alumnos en el colegio "c"
    n_c = {c: df_schools.loc[c-1, 'ALUMNADO'] for c in C}

    # Volumen maximo de almacenaje en el colegio "c"
    V_max_c = {c: df_schools.loc[c-1, 'VOLUMEN MAXIMO'] for c in C}

    # Volumen de alimento "a" consumido por el colegio "c" en
    # el día "t"
    v_a_c_t = {(a, c, t): n_c[c] * v_a[a] * df_fs.loc[t, df_foods.loc[a-1, 'ALIMENTO']]
               for a in A for c in C for t in T if t > 0}

    # Creacion del modelo
    model = Model()

    # Defincion de las variables de decision

    # Variable 1
    # Volumen de alimento "a" que se traslada desde el CA al colegio "c"
    # en el dia "t"
    X_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='X_a_c_t')

    # Variable 2
    # Variable binaria que indica si se envía el alimento "a" al colegio
    # "c" al inicio del día "t":
    x_a_c_t = model.addVars(A, C, T, vtype=GRB.BINARY, name='x_a_c_t')

    # Variable 3
    # Volumen del alimento "a" en el colegio "c" al final del dia $t$
    # que se vence en "t_v" días
    Y_a_c_t_t_v = model.addVars(
        A, C, T, T_V, vtype=GRB.INTEGER, name='Y_a_c_t_t_v')

    # Variable 4
    # Volumen de alimento "a" en el colegio "c" al final del dia "t"
    Z_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='Z_a_c_t')

    # Variable 5
    # Volumen del alimento $a$ en el colegio $c$ consumido durante el
    # dia (después del inicio y antes del final) $t$ que se vencía en
    # $t_v$ días:
    W_a_c_t_t_v = model.addVars(
        A, C, T, T_V, vtype=GRB.INTEGER, name='W_a_c_t_t_v')

    # Funcion objetivo

    model.setObjective(
        quicksum(Y_a_c_t_t_v[a, c, t, 0]
                 for a in A for c in C for t in T if t > 0),
        GRB.MINIMIZE)

    # Definicion de restricciones

    # Restriccion 1
    # Volumen al final del dia 0 de todos los colegios es 0
    model.addConstrs(
        (Z_a_c_t[a, c, 0] == 0 for a in A for c in C),
        name='r1')

    # Restriccion 2
    # El volumen del alimento $a$ en el colegio $t$ al final del dia $t$ 
    # es el volumen al final del dia $(t-1)$ mas el volumen que llego al 
    # inicio del dia $t$ menos el volumen que se consumió durante el dia 
    # $t$ menos el volumen que se echa a perder al final del dia $t$, i.e. 
    # $Y_{a,c,t,0}$
    model.addConstrs(
        (Z_a_c_t[a, c, t] == Z_a_c_t[a, c, t-1] + X_a_c_t[a, c, t] -
         v_a_c_t[a, c, t] - Y_a_c_t_t_v[a, c, t, 0]
         for a in A for c in C for t in T if t > 0),
        name='r2')

    # Restriccion 3
    # El volumen del alimento $a$ en el colegio $t$ al final del dia $t$ 
    # es la suma de los volúmenes de cada alimento $a$ al final del dia 
    # $t$ que se vencen en una cantidad de días mayores a $0$:
    model.addConstrs(
        (Z_a_c_t[a, c, t] == quicksum(Y_a_c_t_t_v[a, c, t, t_v]
                                      for t_v in T_V if t_v > 0)
         for a in A for c in C for t in T if t > 0),
        name='r3')

    # Restriccion 4
    # El volumen del alimento $a$ en el colegio $c$ al final del dia $t$ 
    # que se vence en $c_a$ dias es igual al alimento $a$ que llego al 
    # inicio del dia $t$ menos el alimento que se consumió durante el dia 
    # $t$:
    model.addConstrs(
        (Y_a_c_t_t_v[a, c, t, t_v] == X_a_c_t[a, c, t] - W_a_c_t_t_v[a, c, t, t_v]
         for a in A for c in C for t in T for t_v in T_V if t_v > 0 and t > 0),
        name='r4')

    # Restriccion 5
    # El volumen del alimento $a$ en el colegio $c$ el dia $t$ que se vence en 
    # $t_v$ días es igual al volumen del alimento $a$ en el colegio $c$ el dia 
    # $t-1$ que se vence en $t_v+1$ días menos lo que se consumió de este mismo 
    # alimento durante el dia $t$
    model.addConstrs(
        (Y_a_c_t_t_v[a, c, t, t_v] == Y_a_c_t_t_v[a, c, t-1, t_v+1] - W_a_c_t_t_v[a, c, t, t_v]
         for a in A for c in C for t in T for t_v in T_V[1:-1] if t > 0),
        name='r5')

    # Restriccion 6
    # El volumen de lo que se consume del alimento $a$ en el colegio $c$ durante el 
    # dia $t$ es igual a la suma de los volúmenes del alimentos $a$ que se consumen 
    # en el dia $t$ y que se venían venciendo en $t_v$ días
    model.addConstrs(
        (v_a_c_t[a, c, t] == quicksum(W_a_c_t_t_v[a, c, t, t_v]
                                      for t_v in T_V)
         for a in A for c in C for t in T if t > 0),
        name='r6')

    # Restriccion 7
    # El volumen del alimento $a$ en el colegio $c$ al final del dia $t$ no debe 
    # superar  al volumen máximo de almacenaje del colegio $c$
    model.addConstrs(
        (Z_a_c_t[a, c, t] <= V_max_c[c]
         for a in A for c in C for t in T),
        name='r7')

    # Restriccion 8
    # Cada envío de alimentos debe tener un volumen por debajo del max total y por
    # encima del min total
    model.addConstrs(
        (quicksum(X_a_c_t[a, c, t]
         for a in A) <= V_max for c in C for t in T if t > 0),
        name='r8_1')
    model.addConstrs(
        (quicksum(X_a_c_t[a, c, t]
         for a in A) >= V_min for c in C for t in T if t > 0),
        name='r8_2')

    # Restriccion 9
    # Cada envío de alimentos debe tener un peso por debajo del peso máximo
    model.addConstrs(
        (quicksum(d_a[a] * X_a_c_t[a, c, t]
         for a in A) <= P_max for c in C for t in T if t > 0),
        name='r9')

    # Restriccion 10
    # No se puede hacer un envío de alimentos si no se ha cumplido
    # el tiempo mínimo entre pedidos
    model.addConstrs(
        (quicksum(x_a_c_t[a, c, t2] for t2 in T if t1 <= t2 <= t1 + t_min_c[c]) <= 1
         for a in A for c in C for t1 in T if 0 < t1 < T[-1] - t_min_c[c]),
        name='r10')

    # Restriccion 11
    # No se hizo un envio del alimento "a" el dia t, es decir "x_{a,c,t} = 0",
    # si y solo si
    # el volumen de alimento "a" que llega al colegio "c" al inicio del día "t"
    # igual a 0
    model.addConstrs(
        (x_a_c_t[a, c, t] <= X_a_c_t[a, c, t]
         for a in A for c in C for t in T if t > 0),
        name='r11_1')

    model.addConstrs(
        (INF*x_a_c_t[a, c, t] >= X_a_c_t[a, c, t]
         for a in A for c in C for t in T if t > 0),
        name='r11_2')

    #                 r_7_1   |  r_7_2
    # x = 0 -> X = 0   PASS   |  CHECK
    # x = 1 -> X > 0   CHECK  |  PASS
    # X = 0 -> x = 0   CHECK  |  PASS
    # X > 0 -> x = 1   PASS   |  CHECK

    # Restricciones de naturalezas de las variables

    # Restriccion 11
    # Las variables "X_{a,c,t}" son no negativas
    model.addConstrs(
        (X_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T),
        name='r11')

    # Restriccion 12
    # Las variables "Y_{a,c,t, t_v}" son no negativas
    model.addConstrs(
        (Y_a_c_t_t_v[a, c, t, t_v] >= 0 for a in A for c in C for t in T for t_v in T_V),
        name='r12')

    # Restriccion 13
    # Las variables "Z_{a,c,t}" son no negativas
    model.addConstrs(
        (Z_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T),
        name='r13')

    # Restriccion 14
    # Las variables "W_{a,c,t,t_v}" son no negativas
    model.addConstrs(
        (W_a_c_t_t_v[a, c, t, t_v] >=
         0 for a in A for c in C for t in T for t_v in T_V),
        name='r14')

    # Optimizamos
    model.optimize()
    # model.computeIIS()
    # model.setParam('TimeLimit', 5*60)
    # model.write("model.ilp")

    # Imprimimos la solucion
    if model.status == GRB.Status.OPTIMAL:
        # Guardar en solution.txt  los envios
        # hechos a cada colegio mayores a 0
        with open('solution.txt', 'w') as f:
            for c in C:
                f.write('Colegio: {}\n'.format(c))
                for t in T[1:]:
                    for a in A:
                        if X_a_c_t[a, c, t].x > 0:
                            f.write('Se envia {} de {} en el dia {}\n'.format(
                                X_a_c_t[a, c, t].x, df_foods.loc[a-1, 'ALIMENTO'], t))
                f.write('-'*20 + '\n')
