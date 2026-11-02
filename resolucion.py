"""Resolución resumida de cada método con los datos cargados.
Las funciones devuelven tablas o frases; app.py solo las muestra."""
import numpy as np
import pandas as pd

from interpolacion import diferencias_divididas
from raices import biseccion


def g(v):
    return f"{float(v):.6g}"


def p(v):
    """Número entre paréntesis si es negativo, para que las fórmulas se lean bien."""
    return f"({g(v)})" if float(v) < 0 else g(v)


# ----------------------------- Interpolación -----------------------------
def terminos_lagrange(x, y, xq):
    """Tabla con cada término yᵢ·Lᵢ(x). Devuelve (DataFrame, suma)."""
    filas = []
    for i in range(len(x)):
        Li = 1.0
        for j in range(len(x)):
            if j != i:
                Li *= (xq - x[j]) / (x[i] - x[j])
        filas.append((i, x[i], y[i], Li, y[i] * Li))
    df = pd.DataFrame(filas, columns=["i", "xᵢ", "yᵢ", "Lᵢ(x)", "yᵢ·Lᵢ(x)"])
    return df, float(df["yᵢ·Lᵢ(x)"].sum())


def terminos_newton(x, y, xq):
    """Tabla con cada término cₖ·∏(x − xⱼ). Devuelve (DataFrame, suma)."""
    c = diferencias_divididas(x, y)[0]
    prod, filas = 1.0, []
    for k in range(len(x)):
        filas.append((k, c[k], prod, c[k] * prod))
        prod *= (xq - x[k])
    df = pd.DataFrame(filas, columns=["k", "cₖ = f[x₀,…,xₖ]", "∏(x − xⱼ), j < k", "término"])
    return df, float(df["término"].sum())


def pasos_spline(x, coef, xq):
    n = len(x) - 1
    k = int(np.clip(np.searchsorted(x, xq) - 1, 0, n - 1))
    a, b, c, d = coef[k]
    dx = xq - x[k]
    val = a + b * dx + c * dx**2 + d * dx**3
    dentro = x[0] <= xq <= x[-1]
    return [
        f"Con los {n + 1} puntos se arma el sistema tridiagonal de los cᵢ (spline natural: S″ = 0 en los extremos) "
        "y de ahí salen a, b, c y d de cada tramo.",
        (f"x = {g(xq)} está en el tramo {k + 1}: [{g(x[k])}, {g(x[k + 1])}]." if dentro else
         f"x = {g(xq)} está fuera del rango de los datos; se extrapola con el polinomio del tramo {k + 1}.")
        + f" Aquí dx = x − xᵢ = {g(dx)}.",
        f"Coeficientes de ese tramo: a = {g(a)}, b = {g(b)}, c = {g(c)}, d = {g(d)}.",
        f"S(x) = a + b·dx + c·dx² + d·dx³ = {g(a)} + {p(b)}·{p(dx)} + {p(c)}·{p(dx)}² + {p(d)}·{p(dx)}³ = {g(val)}.",
    ]


# --------------------------------- Raíces ---------------------------------
def _cierre(filas, ok, r, tol, regla):
    resto = "Las demás iteraciones están en la tabla." if len(filas) > 3 else ""
    if ok:
        return f"{resto.strip()} Se repite hasta que {regla} < {tol:.0e}: en {len(filas)} iteraciones se obtiene x ≈ {r:.10g}.".strip()
    return f"{resto.strip()} No se alcanzó la tolerancia {tol:.0e} en el máximo de iteraciones; la última aproximación es x ≈ {r:.10g}.".strip()


def pasos_biseccion(f, a, b, filas, tol, ok, r, n=3):
    L = [f"Se comprueba el cambio de signo: f({g(a)}) = {g(f(a))} y f({g(b)}) = {g(f(b))}; hay una raíz en [{g(a)}, {g(b)}]."]
    for (k, ak, bk, m, fm, err) in filas[:n]:
        nuevo = f"[{g(ak)}, {g(m)}]" if f(ak) * fm < 0 else f"[{g(m)}, {g(bk)}]"
        L.append(f"Iteración {k}: xₘ = ({g(ak)} + {g(bk)})/2 = {g(m)} y f(xₘ) = {g(fm)}; el cambio de signo queda en {nuevo}.")
    L.append(_cierre(filas, ok, r, tol, "(b − a)/2"))
    return L


def pasos_newton_raphson(f, filas, tol, ok, r, n=3):
    L = ["Se usa xₖ₊₁ = xₖ − f(xₖ)/f′(xₖ); la derivada se aproxima con una diferencia central."]
    for (k, xk, fx, d, xn, err) in filas[:n]:
        L.append(f"Iteración {k}: f({g(xk)}) = {g(fx)} y f′ ≈ {g(d)}, entonces xₖ₊₁ = {g(xk)} − {p(fx)}/{p(d)} = {g(xn)}.")
    L.append(_cierre(filas, ok, r, tol, "|xₖ₊₁ − xₖ|"))
    return L


def pasos_secante(f, filas, tol, ok, r, n=3):
    L = ["Se usa xₖ₊₁ = xₖ − f(xₖ)(xₖ − xₖ₋₁)/(f(xₖ) − f(xₖ₋₁)); no necesita derivada."]
    for (k, x0, x1, x2, f2, err) in filas[:n]:
        f0, f1 = f(x0), f(x1)
        L.append(f"Iteración {k}: xₖ₋₁ = {g(x0)}, xₖ = {g(x1)}, f = {g(f0)} y {g(f1)}; "
                 f"xₖ₊₁ = {g(x1)} − {p(f1)}·({g(x1 - x0)})/({g(f1 - f0)}) = {g(x2)}.")
    L.append(_cierre(filas, ok, r, tol, "|xₖ₊₁ − xₖ|"))
    return L


def pasos_tabla(x, y, evaluar):
    L = ["Se recorren las muestras buscando cambios de signo en y (o valores exactamente 0)."]
    for i in range(len(x) - 1):
        if y[i] == 0:
            L.append(f"En x = {g(x[i])} el dato vale exactamente 0, así que es una raíz.")
        elif y[i] * y[i + 1] < 0:
            r, filas, _ = biseccion(lambda t: float(evaluar(t)[0]), x[i], x[i + 1])
            L.append(f"Entre x = {g(x[i])} (y = {g(y[i])}) y x = {g(x[i + 1])} (y = {g(y[i + 1])}) cambia el signo; "
                     f"se aplica bisección sobre el spline y converge en {len(filas)} iteraciones a x ≈ {g(r)}.")
    if y[-1] == 0:
        L.append(f"En x = {g(x[-1])} el dato vale exactamente 0, así que es una raíz.")
    if len(L) == 1:
        L.append("Ninguna muestra cambia de signo: no se encontró una raíz en estos datos (puede existir una de tangencia).")
    return L
