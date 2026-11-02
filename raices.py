"""Raíces: bisección, Newton-Raphson, secante y búsqueda en datos tabulados."""
import numpy as np


def biseccion(f, a, b, tol=1e-8, max_iter=100):
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
    if df is None:                                   # derivada numérica central
        df = lambda t, h=1e-6: (f(t + h) - f(t - h)) / (2 * h)
    x, filas = x0, []
    for k in range(1, max_iter + 1):
        d = df(x)
        if d == 0:
            raise ValueError("f'(x) = 0: el método no puede continuar.")
        xn = x - f(x) / d
        filas.append((k, x, f(x), d, xn, abs(xn - x)))
        if abs(xn - x) < tol:
            return xn, filas, True
        x = xn
    return x, filas, False


def secante(f, x0, x1, tol=1e-8, max_iter=50):
    filas = []
    for k in range(1, max_iter + 1):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            raise ValueError("f(x0) = f(x1): el método no puede continuar.")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        filas.append((k, x0, x1, x2, f(x2), abs(x2 - x1)))
        if abs(x2 - x1) < tol:
            return x2, filas, True
        x0, x1 = x1, x2
    return x1, filas, False


def raices_en_tabla(x, y, evaluar, tol=1e-8):
    """Detecta cambios de signo entre muestras (x ordenado) y refina con bisección
    sobre la función de interpolación `evaluar` (p. ej. el spline cúbico)."""
    raices = []
    for i in range(len(x) - 1):
        if y[i] == 0:
            raices.append(float(x[i]))
        elif y[i] * y[i + 1] < 0:
            r, _, _ = biseccion(lambda t: float(evaluar(t)[0]), x[i], x[i + 1], tol)
            raices.append(r)
    if y[-1] == 0:
        raices.append(float(x[-1]))
    return raices
