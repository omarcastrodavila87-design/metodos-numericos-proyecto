"""Raíces: bisección, Newton-Raphson, secante, raíces en datos tabulados y un
evaluador seguro para funciones f(x) escritas por el usuario."""
import ast
import numpy as np

_OPERADORES = {ast.Add: np.add, ast.Sub: np.subtract, ast.Mult: np.multiply,
               ast.Div: np.divide, ast.Pow: np.power,
               ast.USub: np.negative, ast.UAdd: np.positive}
_FUNCIONES = {"sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "log": np.log,
              "sqrt": np.sqrt, "abs": np.abs, "arctan": np.arctan, "tanh": np.tanh}
_CONSTANTES = {"pi": np.pi, "e": np.e}
MENSAJE = ("Expresión no válida. Usa la variable x, números, + - * / ** ( ) y las funciones "
           "sin, cos, tan, exp, log, sqrt, abs, arctan, tanh. Multiplica con * (por ejemplo 2*x).")


def compilar_funcion(texto):
    """Convierte un texto como 'x**3 - x - 2' en una función f(x) sin usar eval().
    Solo se aceptan números, la variable x, pi, e, operadores aritméticos y las
    funciones de la lista; cualquier otra cosa produce ValueError."""
    texto = texto.strip().replace("^", "**")
    if not texto:
        raise ValueError("Escribe una función f(x).")
    try:
        arbol = ast.parse(texto, mode="eval")
    except SyntaxError:
        raise ValueError(MENSAJE)

    def ev(n, x):
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id == "x":
                return x
            if n.id in _CONSTANTES:
                return _CONSTANTES[n.id]
        elif isinstance(n, ast.BinOp) and type(n.op) in _OPERADORES:
            return _OPERADORES[type(n.op)](ev(n.left, x), ev(n.right, x))
        elif isinstance(n, ast.UnaryOp) and type(n.op) in _OPERADORES:
            return _OPERADORES[type(n.op)](ev(n.operand, x))
        elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCIONES
              and len(n.args) == 1 and not n.keywords):
            return _FUNCIONES[n.func.id](ev(n.args[0], x))
        raise ValueError(MENSAJE)

    def f(x):
        xa = np.asarray(x, float)
        with np.errstate(all="ignore"):
            r = np.asarray(ev(arbol.body, xa), float) + np.zeros_like(xa)
        return float(r) if r.ndim == 0 else r

    f(1.0)  # valida la expresión antes de usarla
    return f


def biseccion(f, a, b, tol=1e-8, max_iter=100):
    """Devuelve (raíz, filas, convergió). Filas: k, a, b, xm, f(xm), error."""
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise ValueError("f(a) y f(b) deben tener signos opuestos.")
    filas = []
    for k in range(1, max_iter + 1):
        m = (a + b) / 2
        fm = f(m)
        err = (b - a) / 2
        filas.append((k, a, b, m, fm, err))
        if fm == 0 or err < tol:
            return m, filas, True
        if fa * fm < 0:
            b = m
        else:
            a, fa = m, fm
    return m, filas, False


def newton_raphson(f, x0, df=None, tol=1e-8, max_iter=50):
    """Devuelve (raíz, filas, convergió). Filas: k, x, f(x), f'(x), x_siguiente, error."""
    if df is None:                                   # derivada numérica central
        df = lambda t, h=1e-6: (f(t + h) - f(t - h)) / (2 * h)
    x, filas = x0, []
    for k in range(1, max_iter + 1):
        d = df(x)
        if d == 0:
            raise ValueError("f'(x) = 0: el método no puede continuar. Prueba otro valor inicial.")
        xn = x - f(x) / d
        filas.append((k, x, f(x), d, xn, abs(xn - x)))
        if abs(xn - x) < tol:
            return xn, filas, True
        x = xn
    return x, filas, False


def secante(f, x0, x1, tol=1e-8, max_iter=50):
    """Devuelve (raíz, filas, convergió). Filas: k, x0, x1, x2, f(x2), error."""
    filas = []
    for k in range(1, max_iter + 1):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            raise ValueError("f(x0) = f(x1): el método no puede continuar. Prueba otros valores iniciales.")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        filas.append((k, x0, x1, x2, f(x2), abs(x2 - x1)))
        if abs(x2 - x1) < tol:
            return x2, filas, True
        x0, x1 = x1, x2
    return x1, filas, False


def raices_en_tabla(x, y, evaluar, tol=1e-8):
    """Detecta cambios de signo entre muestras (x ordenado) y refina cada raíz
    con bisección sobre la función de interpolación `evaluar` (el spline)."""
    raices = []
    for i in range(len(x) - 1):
        if y[i] == 0:
            raices.append(float(x[i]))
        elif y[i] * y[i + 1] < 0:
            r, _, _ = biseccion(lambda t: float(evaluar(t)[0]), x[i], x[i + 1], tol)
            raices.append(float(r))
    if y[-1] == 0:
        raices.append(float(x[-1]))
    return raices
