# Modelacion

## Conjuntos

- Conjunto de días ($t$)
$$
T = \{0, 1,\ldots,|T|\}
$$
de normal $|T|=31$.

- Conjunto de colegios ($c$)

$$
C =  \{1,\ldots,|C|\}
$$

- Conjunto de alimentos ($a$)

$$
A = \{1,\ldots,|A|\}
$$

## Parámetros

- Cantidad de días que dura cada alimento $a$:

$$
c_a \in \mathbb{N}
$$

- Volumen de cada alimento $a$:

$$
v_a \in \mathbb{N}
$$

- Volumen máximo que se puede trasladar un camion todo colegio (variable global):

$$
V_{max} \in \mathbb{N}
$$

- Volumen mínimo que se puede trasladar un camion todo colegio (variable global):

$$
V_{min} \in \mathbb{N}
$$

- Peso máximo que puede llevar un camión:

$$
P_{max} \in \mathbb{N}
$$

- Densidad de cada alimento $a$:

$$
d_a \in \mathbb{N}
$$

- Tiempo mínimo entre pedidos del colegio $c$ al central (es el número de t días mínimo que un colegio c debe esperar para hacerle un pedido nuevo al CA):

$$
t^c_{min} \in \mathbb{N}
$$

- Cantidad de alumnos en el colegio $c$:

$$
n_c \in \mathbb{N}
$$

- Volumen máximo de almacenaje en el colegio $c$

$$
V_{max}^c \in \mathbb{N}
$$

- Volumen de alimento $a$ consumido por $c$ en el día $t$:

$$
v_{a,c,t} \in \mathbb{N}
$$

## Variables

- Volumen de alimento $a$ que el CA manda al colegio $c$ al inicio del día $t$:

$$
X_{a,c,t} \in \mathbb{N}
$$

- Variable binaria que indica si se envía el alimento $a$ al colegio $c$ al inicio del día $t$:

$$
x_{a,c,t} \in \{0,1\}
$$

- Volumen de alimento $a$ que se echa a perder en el colegio $c$ al final del día $t$:

$$
Y_{a,c,t} \in \mathbb{N}
$$

- Volumen de alimento $a$ en el colegio $c$ al final del dia $t$ (no se cuenta lo echado a perder el dia $t$):

$$
Z_{a,c,t} \in \mathbb{N}
$$

- Volumen del alimento $a$ en el colegio $c$ que llego al inicio del día $t_1$ y que no se ha consumido o desechado al final del día $t_2$:

$$
W_{a,c,t_1,t_2} \in \mathbb{N}
$$

## Funcion objetivo

Minimizar el desperdicio de alimentos:

$$
\min \sum_{a \in A} \sum_{c \in C} \sum_{t \in T} Y_{a,c,t}
$$

## Restricciones

### Restrinciones de volumen por dia

- El volumen al final del dia $0$ de todos los colegios es $0$:

$$
Z_{a,c,0} = 0 \quad \forall a \in A, \forall c \in C
$$

- El volumen al final del dia $t$ de todos los colegios es el volumen al final del dia $t-1$ mas el volumen que llego al inicio del dia $t$ menos el volumen que se consumido en el dia $t$ menos el volumen que se echa a perder al final del dia $t$:

$$
Z_{a,c,t} = Z_{a,c,t-1} + X_{a,c,t} - v_{a,c,t} - Y_{a,c,t} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- El colegio $c$ no puede tener mas volumen de alimento $a$ al final del dia $t$ que el volumen máximo de almacenaje del colegio $c$:

$$
Z_{a,c,t} \leq V_{max}^c \quad \forall a \in A, \forall c \in C, \forall t \in T
$$

### Restricciones de envios de alimentos

- Cada envío de alimentos debe tener un volumen por debajo del max total y por encima del min total:

$$
\sum_{a \in A} X_{a,c,t} \leq V_{max} \quad \forall c \in C, \forall t \in T \setminus \{0\}
$$

$$
\sum_{a \in A} X_{a,c,t} \geq V_{min} \quad \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Cada envío de alimentos debe tener un peso por debajo del peso máximo:

$$
\sum_{a \in A} d_a \cdot X_{a,c,t} \leq P_{max} \quad \forall c \in C, \forall t \in T \setminus \{0\}
$$

- No se puede hacer un envío de alimentos si no se ha cumplido el tiempo mínimo entre pedidos:

$$
\sum_{t_2 \in \{t_1, t_1+1, \ldots, t_1+t^c_{min}\}} x_{a,c,t_2} \leq 1 \quad \forall a \in A, \forall c \in C, \forall t_1 \in \{1, 2, \ldots, |T|-t^c_{min}\}
$$

- Si no se hizo un envío es decir, $x_{a,c,t} = 0$, entonces el volumen de alimento $a$ que llega al colegio $c$ al inicio del día $t$ es $0$:

$$
X_{a,c,t} \leq M \cdot (1 - x_{a,c,t}) \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

con $M$ un numero arbitrariamente grande.

### Restricciones de echado a perder

- No puede haber alimentos que llegaron al colegio $c$ el dia $t_1$ y que no se consumieron o desecharon al final del dia $t_2$ de modo que $t_2 - t_1 > c_a$:

$$
W_{a,c,t_1,t_2} \cdot (t_2 - t_1 - c_a) \leq 0 \quad \forall a \in A, \forall c \in C, \forall t_1 \in T, \forall t_2 \in T \setminus \{0\}
$$

Explicación:

1. Si $t_2 - t_1 > c_a$ entonces $W_{a,c,t_1,t_2} \leq 0$ y por lo tanto no queda alimentos del dia $t_1$ que no se consumieron o desecharon al final del dia $t_2$.

2. Por otro lado, si $t_2 - t_1 \leq c_a$ entonces $W_{a,c,t_1,t_2} \geq 0$ y por lo tanto queda alimentos del dia $t_1$ que no se consumieron o desecharon al final del dia $t_2$, que no afecta en nada porque se puede consumir perder al final del dia $t_2$.

### Restriciones de alimento que aun no se consume o desecha

- El volumen almacenado al final del dia $t$ es igual a la suma de los volúmenes que llegaron al inicio los días anteriores o igual al dia $t$ y que no se consumieron o desecharon al final de estos:

$$
Z_{a,c,t} = \sum_{ \{ t_1 \in T \mid t_1 \leq t \} } W_{a,c,t_1,t} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Asignamos $0$ a todos los $W_{a,c,t_1,t_2}$ que no se usan:

$$
W_{a,c,t_1,t_2} = 0 \quad \forall a \in A, \forall c \in C, \forall t_1 \in T, \forall t_2 \in T \setminus \{ t_2 \mid t_2 \leq t_1 \}
$$

## Naturaleza de las variables

- Volumen de alimento $a$ que llega al colegio $c$ al inicio del dia $t$.

$$
X_{a,c,t} \in \mathbb{N} \cup \{ 0 \} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Indica si se hace un envío de alimentos al colegio $c$ el dia $t$.

$$
x_{a,c,t} \in \{ 0, 1 \} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Volumen de alimento $a$ que llega al colegio $c$ al inicio del dia $t$.

$$
Y_{a,c,t} \in \mathbb{N} \cup \{ 0 \} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Volumen de alimento $a$ en el colegio $c$ al final del dia $t$ (no se cuenta lo echado a perder el dia $t$):

$$
Z_{a,c,t} \in \mathbb{N} \cup \{ 0 \} \quad \forall a \in A, \forall c \in C, \forall t \in T
$$

- Volumen del alimento $a$ en el colegio $c$ que llego al inicio del día $t_1$ y que no se ha consumido o desechado al final del día $t_2$:

$$
W_{a,c,t_1,t_2} \in \mathbb{N} \cup \{ 0 \} \quad \forall a \in A, \forall c \in C, \forall t_1 \in T, \forall t_2 \in T \setminus \{0\}
$$
