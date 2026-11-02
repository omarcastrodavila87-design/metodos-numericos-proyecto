"""Interpolación: Lagrange, Newton (diferencias divididas) y spline cúbico natural."""
import numpy as np


def _validar(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("x e y deben tener la misma longitud (mínimo 2 puntos).")
    if len(np.unique(x)) != len(x):
        raise ValueError("Hay valores repetidos en x: se requieren nodos distintos.")
    return x, y


def lagrange(x, y, xq):
    x, y = _validar(x, y)
    xq = np.atleast_1d(np.asarray(xq, float))
    res = np.zeros_like(xq)
    for i in range(len(x)):
        Li = np.ones_like(xq)
        for j in range(len(x)):
            if j != i:
                Li *= (xq - x[j]) / (x[i] - x[j])
        res += y[i] * Li
    return res


def diferencias_divididas(x, y):
    """Tabla triangular; la fila 0 contiene los coeficientes de Newton."""
    x, y = _validar(x, y)
    n = len(x)
    T = np.zeros((n, n))
    T[:, 0] = y
    for j in range(1, n):
        T[:n - j, j] = (T[1:n - j + 1, j - 1] - T[:n - j, j - 1]) / (x[j:] - x[:n - j])
    return T


def newton(x, y, xq):
    x, y = _validar(x, y)
    c = diferencias_divididas(x, y)[0]
    xq = np.atleast_1d(np.asarray(xq, float))
    res = np.full_like(xq, c[-1])
    for k in range(len(x) - 2, -1, -1):      # esquema de Horner
        res = res * (xq - x[k]) + c[k]
    return res


def spline_cubico(x, y):
    """Spline cúbico natural (S''=0 en los extremos).
    Devuelve (evaluar, x_ordenado, coef) con S_i(t) = a + b·dx + c·dx² + d·dx³."""
    x, y = _validar(x, y)
    o = np.argsort(x)
    x, y = x[o], y[o]
    n, h = len(x) - 1, np.diff(x)
    A, r = np.zeros((n + 1, n + 1)), np.zeros(n + 1)
    A[0, 0] = A[n, n] = 1
    for i in range(1, n):
        A[i, i - 1:i + 2] = [h[i - 1], 2 * (h[i - 1] + h[i]), h[i]]
        r[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
    c = np.linalg.solve(A, r)
    b = np.diff(y) / h - h * (2 * c[:-1] + c[1:]) / 3
    d = np.diff(c) / (3 * h)
    coef = np.column_stack([y[:-1], b, c[:-1], d])

    def evaluar(xq):
        xq = np.atleast_1d(np.asarray(xq, float))
        k = np.clip(np.searchsorted(x, xq) - 1, 0, n - 1)
        dx = xq - x[k]
        return coef[k, 0] + coef[k, 1] * dx + coef[k, 2] * dx**2 + coef[k, 3] * dx**3

    return evaluar, x, coef
