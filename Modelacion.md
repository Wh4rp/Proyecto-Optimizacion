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

- Conjunto del alimentos ($a$)

$$
A = \{1,\ldots,|A|\}
$$

## Parámetros

- Cantidad de días que dura cada alimento $a$ antes de vencerse:

$$
c_a \in \mathbb{N}
$$

- Volumen de cada alimento $a$:

$$
v_a \in \mathbb{N}
$$

- Volumen máximo que puede transportar un camion a cualquier colegio (variable global):

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

- Tiempo mínimo entre pedidos del colegio $c$ a a central (es el número de t días mínimo que un colegio c debe esperar para hacerle un pedido nuevo al CA):

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

- Volumen del alimento $a$ consumido por $c$ en el día $t$:

$$
v_{a,c,t} \in \mathbb{N}
$$

## Variables

- Volumen del alimento $a$ que la CA envia al colegio $c$ al inicio del día $t$:

$$
X_{a,c,t} \in \mathbb{N}
$$

- Variable binaria que indica si se envía el alimento $a$ al colegio $c$ al inicio del día $t$:

$$
x_{a,c,t} \in \{0,1\}
$$

- Volumen del alimento $a$ en el colegio $c$ al final del dia $t$ que se vence en $t_v$ días:

$$
Y_{a,c,t,t_v} \in \mathbb{N}
$$

si $t_v$ es igual a $0$ quiere decir que se vence en el dia $t$.

- Volumen del alimento $a$ en el colegio $c$ al final del dia $t$ (no se cuenta el alimento que se vence en el dia $t$):

$$
Z_{a,c,t} \in \mathbb{N}
$$

- Volumen del alimento $a$ en el colegio $c$ consumido durante el dia (después del inicio y antes del final) $t$ que se vencía en $t_v$ días:

$$
W_{a,c,t,t_v} \in \mathbb{N}
$$

## Función objetivo

Minimizar el desperdicio del alimentos:

$$
\min \sum_{a \in A} \sum_{c \in C} \sum_{t \in T} Y_{a,c,t,0}
$$

## Restricciones

### Restricciones de volumen por dia

- El volumen al final del dia $0$ de todos los colegios es $0$:

$$
Z_{a,c,0} = 0 \quad \forall a \in A, \forall c \in C
$$

- El volumen del alimento $a$ en el colegio $t$ al final del dia $t$ es el volumen al final del dia $(t-1)$ mas el volumen que llego al inicio del dia $t$ menos el volumen que se consumió durante el dia $t$ menos el volumen que se echa a perder al final del dia $t$, i.e. $Y_{a,c,t,0}$:

$$
Z_{a,c,t} = Z_{a,c,t-1} + X_{a,c,t} - v_{a,c,t} - Y_{a,c,t,0} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- El volumen del alimento $a$ en el colegio $t$ al final del dia $t$ es la suma de los volúmenes de cada alimento $a$ al final del dia $t$ que se vencen en una cantidad de días mayores a $0$:

$$
Z_{a,c,t} = \sum_{t_v \in T \setminus \{ 0 \} } Y_{a,c,t,t_v} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- El volumen del alimento $a$ en el colegio $c$ al final del dia $t$ que se vence en $c_a$ dias es igual al alimento $a$ que llego al inicio del dia $t$ menos el alimento que se consumió durante el dia $t$:

$$
Y_{a,c,t,c_a} = X_{a,c,t} - W_{a,c,t,c_a} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- El volumen del alimento $a$ en el colegio $c$ el dia $t$ que se vence en $t_v$ días es igual al volumen del alimento $a$ en el colegio $c$ el dia $t-1$ que se vence en $t_v+1$ días menos lo que se consumió de este mismo alimento durante el dia $t$:

$$
Y_{a,c,t,t_v} = Y_{a,c,t-1,t_v+1} - W_{a,c,t,t_v} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}, \forall t_v \in T \setminus \{0\}
$$

- El volumen de lo que se consume del alimento $a$ en el colegio $c$ durante el dia $t$ es igual a la suma de los volúmenes del alimento $a$ que se consumen en el dia $t$ y que se venían venciendo en $t_v$ días:

$$
v_{a,c,t} = \sum_{t_v \in T } W_{a,c,t,t_v} \quad \forall a \in A, \forall c \in C, \forall t \in T
$$

- El volumen del alimento $a$ en el colegio $c$ al final del dia $t$ no debe superar al volumen máximo de almacenaje del colegio $c$:

$$
Z_{a,c,t} \leq V_{max}^c \quad \forall a \in A, \forall c \in C, \forall t \in T
$$

### Restricciones de envíos

- Cada envío de alimentos debe tener un volumen por debajo del máximo y por encima del minino volumen por camion:

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
\sum_{t_v \in \{t, t+1, \ldots, t+t^c_{min}\}} x_{a,c,t_v} \leq 1 \quad \forall a \in A, \forall c \in C, \forall t \in \{1, 2, \ldots, |T|-t^c_{min}\}
$$

- No se hizo un envío del alimento $a$ el dia $t$, es decir $x_{a,c,t} = 0$, si y solo si el volumen del alimento $a$ que se envía al colegio $c$ al inicio del día "t" es igual a 0:

$$
x_{a,c,t} \leq X_{a,c,t} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

y,

$$
M \cdot x_{a,c,t} \geq X_{a,c,t} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

con $M$ un numero arbitrariamente grande.

## Naturaleza de las variables

- Volumen del alimento $a$ que la CA manda al colegio $c$ al inicio del día $t$:

$$
X_{a,c,t} \in \mathbb{N} \cup \{0\} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Variable binaria que indica si se envía el alimento $a$ al colegio $c$ al inicio del día $t$:

$$
x_{a,c,t} \in \{0,1\} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}
$$

- Volumen del alimento $a$ en el colegio $c$ al final del dia $t$ que se vence en $t_v$ días:

$$
Y_{a,c,t,t_v} \in \mathbb{N} \cup \{0\} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}, \forall t_v \in T \setminus \{0\}
$$

- Volumen del alimento $a$ en el colegio $c$ al final del dia $t$ (no se cuenta el alimento que se vence en el dia $t$):

$$
Z_{a,c,t} \in \mathbb{N} \cup \{0\} \quad \forall a \in A, \forall c \in C, \forall t \in T
$$

- Volumen del alimento $a$ en el colegio $c$ consumido durante el dia (después del inicio y antes del final) $t$ que se vencía en $t_v$ días:

$$
W_{a,c,t,t_v} \in \mathbb{N} \cup \{0\} \quad \forall a \in A, \forall c \in C, \forall t \in T \setminus \{0\}, \forall t_v \in T \setminus \{0\}
$$
