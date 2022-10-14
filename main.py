from gurobipy import Model, GRB, quicksum
from gurobipy.GRB import INFINITY as INF
from minuta import load_data

if __name__ == '__main__':
    df_am, df_foods, df_schools = load_data(
        'alimentation-monthly.csv', 'foods.csv', 'colegios.csv')

    print(df_foods)
    print(len(df_foods['DIAS CADUCIDAD']))

    # Definicion de los conjuntos

    T = range(0, 32)  # Dias del mes
    C = range(1, 4)  # Colegios
    A = range(1, len(df_foods['ALIMENTO'])+1)  # Alimentos

    # Definicion de los parametros

    # Dias de caducidad
    c_a = {a: df_foods.loc[a-1, 'DIAS CADUCIDAD'] for a in A}

    # Volumen de cada alimento
    v_a = {a: df_foods.loc[a-1, 'VOLUMEN'] for a in A}

    # Volumen máximo que se puede trasladar desde CA
    V_max = 1000

    # Volumen mínimo que se puede trasladar desde CA
    V_min = 100

    # Peso máximo que puede llevar un camión
    P_max = 1000

    # Densidad de cada alimento "a"
    d_a = {a: df_foods.loc[a-1, 'DENSIDAD'] for a in A}

    # Tiempo mínimo entre pedidos del colegio "c" al CA
    t_min = {c: df_schools.loc[c-1, 'TIEMPO MINIMO'] for c in C}

    # Cantidad de alumnos en el colegio "c"
    n_c = {c: df_schools.loc[c-1, 'NUMERO ALUMNOS'] for c in C}

    # Volumen maximo de almacenaje en el colegio "c"
    V_max_c = {c: df_schools.loc[c-1, 'VOLUMEN MAXIMO'] for c in C}

    # Volumen de alimento "a" consumido por el colegio "c" en
    # el día "t"
    v_a_c_t = {(a, c, t): df_foods.loc[c-1, 'CANTIDAD ALUMNOS']
         * df_foods.loc[a-1, 'VOLUMEN']
         * df_am.loc[t-1, df_foods.loc[a-1, 'ALIMENTO']] for c in C for t in T for a in A}

    # Creacion del modelo
    model = Model()

    # Defincion de las variables de decision
    
    # Volumen de alimento "a" que se traslada desde el CA al colegio "c" 
    # en el dia "t"
    X_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='X_a_c_t')

    # Variable binaria que indica si se envía el alimento $a$ al colegio 
    # $c$ al inicio del día $t$:
    x_a_c_t = model.addVars(A, C, T, vtype=GRB.BINARY, name='x_a_c_t')

    # Volumen de alimento "a" que se echó a perder en el colegio "c"
    # en el dia "t"
    Y_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='Y_a_c_t')

    # Volumen de alimento "a" en el colegio "c" en el dia "t"
    Z_a_c_t = model.addVars(A, C, T, vtype=GRB.INTEGER, name='Z_a_c_t')

    # Volumen del alimento "a" en el colegio "c" que llego en el dia "t_1"
    # y que aun no se ha consumido o desechado en el dia "t_2"
    W_a_c_t1_t2 = model.addVars(A, C, T, T, vtype=GRB.INTEGER, name='W_a_c_t1_t2')

    # Funcion objetivo

    model.setObjective(
        quicksum(Y_a_c_t[a, c, t] for a in A for c in C for t in T),
        GRB.MINIMIZE)

    # Definicion de restricciones
    
    # Restriccion 1
    # Volumen al final del dia 0 de todos los colegios es 0
    model.addConstrs(
        (Z_a_c_t[a, c, 0] == 0 for a in A for c in C),
        name='r1')
    
    # Restriccion 2
    # El volumen al final del dia $t$ de todos los colegios es el volumen 
    # al final del dia "t-1" mas el volumen que llego al inicio del dia "t" 
    # menos el volumen que se consumido en el dia "t" menos el volumen que 
    # se echa a perder al final del dia "t":
    model.addConstrs(
        (Z_a_c_t[a, c, t] == Z_a_c_t[a, c, t-1] + X_a_c_t[a, c, t] 
        - v_a_c_t[a, c, t] - Y_a_c_t[a, c, t]
            for a in A for c in C for t in T if t > 0),
        name='r2')
    
    # Restriccion 3
    # El colegio $c$ no puede tener mas volumen de alimento $a$ al final 
    # del dia $t$ que el volumen máximo de almacenaje del colegio $c$:
    model.addConstrs(
        (Z_a_c_t[a, c, t] <= V_max_c[c] for a in A for c in C for t in T),
        name='r3')
    
    # Restriccion 4
    # Cada envío de alimentos debe tener un volumen por debajo del max total y por 
    # encima del min total
    model.addConstrs(
        (quicksum(X_a_c_t[a, c, t] for a in A) <= V_max for c in C for t in T if t > 0),
        name='r4_1')
    model.addConstrs(
        (quicksum(X_a_c_t[a, c, t] for a in A) >= V_min for c in C for t in T if t > 0),
        name='r4_2')
    
    # Restriccion 5
    # Cada envío de alimentos debe tener un peso por debajo del peso máximo
    model.addConstrs(
        (quicksum(d_a[a] * X_a_c_t[a, c, t] for a in A) <= P_max for c in C for t in T if t > 0),
        name='r5')

    # Restriccion 6
    # No se puede hacer un envío de alimentos si no se ha cumplido 
    # el tiempo mínimo entre pedidos
    model.addConstrs(
        (quicksum(x_a_c_t[a, c, t2] for t2 in T if t1 <= t2 <= t1 + t_min[c]) <= 1 
        for c in C for a in A for t1 in T if 0 < t1 < T[-1] - t_min[c]),
        name='r6')
    
    # Restriccion 7
    # Si no se hizo un envío es decir, $x_{a,c,t} = 0$, entonces el volumen 
    # de alimento $a$ que llega al colegio $c$ al inicio del día $t$ es $0$

    model.addConstrs(
        (X_a_c_t[a, c, t] <= INF*(1 - x_a_c_t[a, c, t]) for a in A for c in C for t in T if t > 0),
        name='r7_1')
    
    # Restriccion 8
    # No puede haber alimentos que llegaron al colegio $c$ el dia $t_1$ y que no 
    # se consumieron o desecharon al final del dia $t_2$ de modo que 
    # $t_2 - t_1 > c_a$

    model.addConstrs(
        (W_a_c_t1_t2[a, c, t1, t2] * (t2 - t1 - c_a[a]) <= 0 for a in A for c in C for t1 in T for t2 in T if t1 < t2),
        name='r8')
    
    # Restriccion 9
    # El volumen almacenado al final del dia $t$ es igual a la suma de los 
    # volúmenes que llegaron al inicio los días anteriores o igual al dia 
    # $t$ y que no se consumieron o desecharon al final de estos
    model.addConstrs(
        (Z_a_c_t[a, c, t] == quicksum(W_a_c_t1_t2[a, c, t1, t] for t1 in T if t1 <= t) for a in A for c in C for t in T if t > 0),
        name='r9')
    
    # Restriccion 10
    # Asignamos $0$ a todos los $w_{a,c,t_1,t_2}$ que no se usan
    model.addConstrs(
        (W_a_c_t1_t2[a, c, t1, t2] == 0 for a in A for c in C for t1 in T for t2 in T if t1 > t2),
        name='r10')
    
    # Restricciones de naturalezas de las variables

    # Restriccion 11
    # Las variables $X_{a,c,t}$ son no negativas
    model.addConstrs(
        (X_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T if t > 0),
        name='r11')
    
    # Restriccion 12
    # Las variables $Y_{a,c,t}$ son no negativas
    model.addConstrs(
        (Y_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T if t > 0),
        name='r12')
    
    # Restriccion 13
    # Las variables $Z_{a,c,t}$ son no negativas
    model.addConstrs(
        (Z_a_c_t[a, c, t] >= 0 for a in A for c in C for t in T if t > 0),
        name='r13')
