import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from interpolacion import lagrange, newton, spline_cubico, diferencias_divididas
from raices import biseccion, newton_raphson, secante, raices_en_tabla

st.set_page_config(page_title="SignalLab Numérico", layout="wide")
st.title("SignalLab Numérico")

# ---------- Entrada y validación ----------
archivo = st.sidebar.file_uploader("Archivo CSV o Excel", type=["csv", "xlsx"])
if archivo is None:
    st.info("Sube un archivo con al menos dos columnas numéricas.")
    st.stop()
try:
    df = pd.read_csv(archivo) if archivo.name.endswith(".csv") else pd.read_excel(archivo)
except Exception as e:
    st.error(f"No se pudo leer el archivo: {e}")
    st.stop()
num = df.select_dtypes("number").columns.tolist()
if len(num) < 2:
    st.error("El archivo necesita al menos dos columnas numéricas.")
    st.stop()
cx = st.sidebar.selectbox("Variable x", num)
cy = st.sidebar.selectbox("Variable y", [c for c in num if c != cx])
datos = df[[cx, cy]].dropna().sort_values(cx)
x, y = datos[cx].to_numpy(), datos[cy].to_numpy()
st.sidebar.caption(f"{len(x)} puntos válidos")

tab_int, tab_raiz = st.tabs(["Interpolación", "Raíces"])

# ---------- Interpolación ----------
with tab_int:
    metodo = st.radio("Método", ["Lagrange", "Newton", "Spline cúbico"], horizontal=True)
    xq = st.number_input("Evaluar en x =", value=float(np.mean(x)))
    try:
        if metodo == "Spline cúbico":
            f, xs_n, coef = spline_cubico(x, y)
        else:
            f = (lambda t: lagrange(x, y, t)) if metodo == "Lagrange" else (lambda t: newton(x, y, t))
        st.success(f"P({xq:g}) = {f(xq)[0]:.6g}")
        if not (x.min() <= xq <= x.max()):
            st.warning("x está fuera del rango de los datos: es extrapolación y el error puede ser grande.")
        if metodo != "Spline cúbico" and len(x) > 12:
            st.warning("Con muchos nodos el polinomio puede oscilar (fenómeno de Runge); compara con el spline.")
        xs = np.linspace(x.min(), x.max(), 400)
        fig, ax = plt.subplots()
        ax.plot(xs, f(xs), label=metodo)
        ax.scatter(x, y, color="k", zorder=3, label="datos")
        ax.scatter([xq], f(xq), color="r", zorder=4, label="evaluación")
        ax.set_xlabel(cx); ax.set_ylabel(cy); ax.legend(); ax.grid(alpha=.3)
        st.pyplot(fig)
        if metodo == "Newton":
            st.caption("Tabla de diferencias divididas")
            st.dataframe(pd.DataFrame(diferencias_divididas(x, y)))
        if metodo == "Spline cúbico":
            st.caption("Coeficientes por tramo: S(t) = a + b·dx + c·dx² + d·dx³, con dx = t − xᵢ")
            st.dataframe(pd.DataFrame(coef, columns=["a", "b", "c", "d"]))
    except ValueError as e:
        st.error(str(e))

# ---------- Raíces ----------
ESPACIO = {k: getattr(np, k) for k in ("sin", "cos", "tan", "exp", "log", "sqrt", "pi", "e")}

with tab_raiz:
    fuente = st.radio("Función", ["f(x) escrita", "Datos tabulados (spline)"], horizontal=True)
    try:
        if fuente.startswith("Datos"):
            ev = spline_cubico(x, y)[0]
            r = raices_en_tabla(x, y, ev)
            st.write("Raíces encontradas:", [round(v, 8) for v in r] if r else "no hay cambios de signo en los datos.")
        else:
            expr = st.text_input("f(x) =", "x**3 - x - 2")
            f = lambda t: eval(expr, {"__builtins__": {}}, {**ESPACIO, "x": t})
            met = st.selectbox("Método", ["Bisección", "Newton-Raphson", "Secante"])
            tol = st.number_input("Tolerancia", value=1e-8, format="%.0e")
            if met == "Bisección":
                a = st.number_input("a", value=1.0); b = st.number_input("b", value=2.0)
                r, filas, ok = biseccion(f, a, b, tol)
                cols = ["k", "a", "b", "xm", "f(xm)", "error"]
            elif met == "Newton-Raphson":
                x0 = st.number_input("x0", value=1.5)
                r, filas, ok = newton_raphson(f, x0, tol=tol)
                cols = ["k", "x", "f(x)", "f'(x)", "x siguiente", "error"]
            else:
                x0 = st.number_input("x0", value=1.0); x1 = st.number_input("x1", value=2.0)
                r, filas, ok = secante(f, x0, x1, tol)
                cols = ["k", "x0", "x1", "x2", "f(x2)", "error"]
            (st.success if ok else st.warning)(f"Raíz ≈ {r:.10g}" + ("" if ok else " (no convergió en el máximo de iteraciones)"))
            st.dataframe(pd.DataFrame(filas, columns=cols))
    except Exception as e:
        st.error(f"Revisa los datos de entrada: {e}")
