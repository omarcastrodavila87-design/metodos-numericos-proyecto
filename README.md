# SignalLab Numérico

Aplicación web hecha con Streamlit para analizar datos tabulados con métodos numéricos.
Proyecto del curso **Métodos Numéricos** · Facultad de Ingeniería Electrónica y Eléctrica (FIEE), UNMSM.

**App:** https://signallab-mnum-ricos-hebaeb7aw24xenujqpyblt.streamlit.app/

## Qué hace

| Módulo | Métodos |
|---|---|
| Interpolación | Lagrange, Newton (diferencias divididas) y spline cúbico natural |
| Raíces | Bisección, Newton-Raphson, secante y raíces de datos tabulados (spline + bisección) |

La interfaz tiene una barra lateral para cargar los datos y dos pestañas, **Interpolación** y **Raíces**.
Cada método muestra su gráfica, su tabla y una **resolución resumida** que usa los datos cargados
(se puede ocultar con la casilla de la barra lateral):

- Lagrange y Newton: aporte de cada nodo o término en el valor de x pedido.
- Spline cúbico: tramo elegido, coeficientes y sustitución en S(x).
- Bisección, Newton-Raphson y secante: las primeras iteraciones con sus números y el resultado final.
- Datos tabulados: intervalos con cambio de signo y la raíz refinada en cada uno.

## Archivos

- `app.py`: interfaz de Streamlit.
- `interpolacion.py`: `lagrange`, `newton`, `diferencias_divididas`, `spline_cubico`.
- `raices.py`: `biseccion`, `newton_raphson`, `secante`, `raices_en_tabla` y `compilar_funcion` (lee f(x) sin usar `eval`).
- `resolucion.py`: textos y tablas de la resolución resumida.
- `estilo.py`: fondo y banner de la FIEE-UNMSM.
- `requirements.txt`: librerías necesarias.
- `datos_ejemplo.csv` (opcional): si existe, se usa como datos de ejemplo; si no, la app trae una señal de ejemplo integrada.
- `fondo_fiee.jpg` (opcional): foto de la facultad para usar como fondo. Si no existe, se usa un fondo de circuitos y ondas generado por código. Pesa menos de 1,5 MB.
- `logo_fiee.png` (opcional): logo que aparece en el banner.

## Cómo usarla

1. Sube un archivo CSV o Excel con al menos dos columnas numéricas (o usa los datos de ejemplo).
2. Elige las variables x e y en la barra lateral.
3. En **Interpolación**, elige el método y el valor de x a evaluar.
4. En **Raíces**, escribe f(x) (por ejemplo `x**3 - x - 2`) o busca las raíces de tus datos.

## Ejecutar en tu computadora

```
pip install -r requirements.txt
streamlit run app.py
```

## Validaciones y límites

- Se necesitan al menos dos columnas numéricas y dos filas con valores en x e y; las filas vacías se omiten.
- Los valores repetidos en x se rechazan con un mensaje de error.
- La app avisa si se extrapola (x fuera del rango) y si Lagrange o Newton usan más de 12 nodos (fenómeno de Runge).
- El spline es natural (segunda derivada igual a cero en los extremos).
- La bisección exige f(a)·f(b) < 0. En datos tabulados, una raíz sin cambio de signo (de tangencia) no se detecta.
- En f(x) se permiten: x, números, `+ - * / **`, `pi`, `e` y las funciones `sin cos tan exp log sqrt abs arctan tanh`.
