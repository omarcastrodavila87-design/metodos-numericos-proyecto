"""SignalLab Numérico — segundo avance (Métodos Numéricos), FIEE-UNMSM.
Dos módulos: Interpolación (Lagrange o Newton, y spline cúbico) y Raíces."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="SignalLab Numérico · FIEE-UNMSM", page_icon="⚡", layout="wide")

import estilo
import resolucion as rs
from interpolacion import lagrange, newton, spline_cubico, diferencias_divididas
from raices import biseccion, newton_raphson, secante, raices_en_tabla, compilar_funcion

estilo.aplicar_fondo()
estilo.banner("SignalLab Numérico", "Interpolación y raíces sobre datos tabulados · curso Métodos Numéricos")


def datos_ejemplo():
    """datos_ejemplo.csv del repositorio; si no existe o no se puede leer, usa una señal amortiguada."""
    try:
        return pd.read_csv(Path(__file__).with_name("datos_ejemplo.csv"))
    except Exception:
        t = np.arange(0, 6.5, 0.5)
        return pd.DataFrame({"tiempo_s": t, "voltaje_V": np.round(5 * np.exp(-0.3 * t) * np.cos(1.5 * t), 3)})


def mostrar(fig):
    st.pyplot(fig)
    plt.close(fig)


def tabla(df, formato="{:.8g}", alto=None):
    st.dataframe(df.style.format(formato, na_rep=""), hide_index=True)


def lista(pasos):
    st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(pasos, 1)))


# ======================= Barra lateral: entrada y validación =======================
with st.sidebar:
    st.header("Datos")
    archivo = st.file_uploader("Subir CSV / Excel", type=["csv", "xlsx"])
    try:
        if archivo is None:
            df = datos_ejemplo()
            st.caption("Sin archivo: se usan datos de ejemplo.")
        else:
            archivo.seek(0)
            if archivo.name.lower().endswith(".csv"):
                df = pd.read_csv(archivo, sep=None, engine="python")   # detecta , o ;
            else:
                df = pd.read_excel(archivo)
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    numericas = df.select_dtypes("number").columns.tolist()
    if len(numericas) < 2:
        st.error("El archivo necesita al menos dos columnas numéricas.")
        st.stop()
    cx = st.selectbox("Variable x", numericas)
    cy = st.selectbox("Variable y", [c for c in numericas if c != cx])

    datos = df[[cx, cy]].dropna().sort_values(cx)
    if len(datos) < 2:
        st.error("Se necesitan al menos 2 filas con valores en x e y.")
        st.stop()
    x, y = datos[cx].to_numpy(float), datos[cy].to_numpy(float)
    st.metric("n.º de puntos válidos", len(x))
    if len(df) > len(datos):
        st.caption(f"Se omitieron {len(df) - len(datos)} filas con valores vacíos.")
    mostrar_res = st.checkbox("Mostrar resolución paso a paso", value=True)

tab_int, tab_raiz = st.tabs(["Interpolación", "Raíces"])

# ============================== Pestaña Interpolación ==============================
with tab_int:
    metodo = st.radio("Método", ["Lagrange", "Newton", "Spline cúbico"], horizontal=True)
    xq = st.number_input("Evaluar en x =", value=float(np.mean(x)), format="%g")
    try:
        coef = None
        if metodo == "Lagrange":
            f = lambda t: lagrange(x, y, t)
        elif metodo == "Newton":
            f = lambda t: newton(x, y, t)
        else:
            f, _, coef = spline_cubico(x, y)
        yq = float(f(xq)[0])
    except ValueError as e:
        st.error(str(e))
    else:
        st.success(f"{metodo}: valor interpolado en x = {xq:g}  →  {yq:.8g}")
        if not (x.min() <= xq <= x.max()):
            st.warning("x está fuera del rango de los datos: es extrapolación y el error puede ser grande.")
        if metodo != "Spline cúbico" and len(x) > 12:
            st.warning("Con muchos nodos el polinomio puede oscilar (fenómeno de Runge); compáralo con el spline.")
        xs = np.linspace(min(x.min(), xq), max(x.max(), xq), 500)
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.plot(xs, f(xs), color="#1f5fa8", label=metodo)
        ax.scatter(x, y, color="black", zorder=3, label="datos")
        ax.scatter([xq], [yq], color="red", zorder=4, label="punto evaluado")
        ax.set_xlabel(cx); ax.set_ylabel(cy); ax.grid(alpha=0.3); ax.legend()
        mostrar(fig)

        if mostrar_res:
            st.markdown("#### Resolución resumida")
            if metodo == "Lagrange":
                st.latex(r"P(x)=\sum_{i=0}^{n} y_i\,L_i(x),\qquad L_i(x)=\prod_{j\neq i}\frac{x-x_j}{x_i-x_j}")
                st.caption(f"Con los {len(x)} nodos se forma un polinomio de grado {len(x) - 1}. Aporte de cada nodo en x = {xq:g}:")
                res, total = rs.terminos_lagrange(x, y, xq)
                tabla(res, alto=min(38 * (len(res) + 1), 300))
                st.markdown(f"P({xq:g}) = Σ yᵢ·Lᵢ(x) = **{total:.8g}**")
            elif metodo == "Newton":
                st.latex(r"P(x)=f[x_0]+f[x_0,x_1](x-x_0)+f[x_0,x_1,x_2](x-x_0)(x-x_1)+\cdots")
                st.caption(f"Los coeficientes cₖ salen de la tabla de diferencias divididas. Aporte de cada término en x = {xq:g}:")
                res, total = rs.terminos_newton(x, y, xq)
                tabla(res, alto=min(38 * (len(res) + 1), 300))
                st.markdown(f"P({xq:g}) = Σ cₖ·∏(x − xⱼ) = **{total:.8g}**")
            else:
                lista(rs.pasos_spline(x, coef, xq))

        if metodo == "Newton":
            st.caption("Tabla de diferencias divididas (la primera fila contiene los coeficientes de Newton)")
            T = diferencias_divididas(x, y)
            n = len(x)
            for j in range(1, n):
                T[n - j:, j] = np.nan
            nombres = [cx, cy] + [f"orden {k}" for k in range(1, n)]
            tabla(pd.DataFrame(np.column_stack([x, T]), columns=nombres), "{:.6g}")
        if metodo == "Spline cúbico":
            st.caption("Coeficientes por tramo: S(t) = a + b·dx + c·dx² + d·dx³, con dx = t − xᵢ")
            c = pd.DataFrame(coef, columns=["a", "b", "c", "d"])
            c.insert(0, "xᵢ", x[:-1]); c.insert(1, "xᵢ₊₁", x[1:])
            tabla(c, "{:.6g}")

# ================================ Pestaña Raíces ================================
with tab_raiz:
    fuente = st.radio("Origen de la función", ["Función f(x) escrita", "Datos tabulados (spline)"], horizontal=True)

    if fuente.startswith("Datos"):
        try:
            ev = spline_cubico(x, y)[0]
            raices = raices_en_tabla(x, y, ev)
        except ValueError as e:
            st.error(str(e))
        else:
            if raices:
                st.success("Raíces aproximadas: " + ", ".join(f"{r:.6g}" for r in raices))
            else:
                st.info("Ninguna muestra cambia de signo. Eso no demuestra que no exista una raíz, solo que los datos no la muestran.")
            xs = np.linspace(x.min(), x.max(), 500)
            fig, ax = plt.subplots(figsize=(7, 3.6))
            ax.plot(xs, ev(xs), color="#1f5fa8", label="spline cúbico")
            ax.scatter(x, y, color="black", zorder=3, label="datos")
            ax.axhline(0, color="gray", lw=0.8)
            if raices:
                ax.scatter(raices, [0] * len(raices), color="red", zorder=4, label="raíces")
            ax.set_xlabel(cx); ax.set_ylabel(cy); ax.grid(alpha=0.3); ax.legend()
            mostrar(fig)
            if mostrar_res:
                st.markdown("#### Resolución resumida")
                lista(rs.pasos_tabla(x, y, ev))
    else:
        texto = st.text_input("f(x) =", "x**3 - x - 2", help="Ejemplos: cos(x) - x, exp(-x) - x, x^2 - 4")
        try:
            f = compilar_funcion(texto)
        except ValueError as e:
            st.error(str(e))
        else:
            met = st.radio("Método", ["Bisección", "Newton-Raphson", "Secante"], horizontal=True)
            tol = st.select_slider("Tolerancia", options=[1e-4, 1e-6, 1e-8, 1e-10, 1e-12], value=1e-8,
                                   format_func=lambda v: f"{v:.0e}")
            try:
                if met == "Bisección":
                    c1, c2 = st.columns(2)
                    a = c1.number_input("a", value=1.0, step=0.1, format="%g")
                    b = c2.number_input("b", value=2.0, step=0.1, format="%g")
                    r, filas, ok = biseccion(f, a, b, tol)
                    cols, puntos = ["k", "a", "b", "xm", "f(xm)", "error"], [a, b]
                    pasos = lambda: rs.pasos_biseccion(f, a, b, filas, tol, ok, r)
                elif met == "Newton-Raphson":
                    x0 = st.number_input("x0", value=1.5, step=0.1, format="%g")
                    r, filas, ok = newton_raphson(f, x0, tol=tol)
                    cols, puntos = ["k", "x_k", "f(x_k)", "f'(x_k)", "x_k+1", "error"], [x0]
                    pasos = lambda: rs.pasos_newton_raphson(f, filas, tol, ok, r)
                else:
                    c1, c2 = st.columns(2)
                    x0 = c1.number_input("x0", value=1.0, step=0.1, format="%g")
                    x1 = c2.number_input("x1", value=2.0, step=0.1, format="%g")
                    r, filas, ok = secante(f, x0, x1, tol)
                    cols, puntos = ["k", "x_k-1", "x_k", "x_k+1", "f(x_k+1)", "error"], [x0, x1]
                    pasos = lambda: rs.pasos_secante(f, filas, tol, ok, r)
            except ValueError as e:
                st.error(str(e))
            else:
                if not np.isfinite(r):
                    st.error("El método divergió (resultado no finito). Cambia los valores iniciales.")
                else:
                    (st.success if ok else st.warning)(
                        f"Raíz aproximada: {r:.10g}   (f(raíz) = {f(r):.2e})"
                        + ("" if ok else " — no se alcanzó la tolerancia en el máximo de iteraciones"))
                    lo, hi = min(puntos + [r]), max(puntos + [r])
                    pad = 0.25 * (hi - lo) or 1.0
                    xs = np.linspace(lo - pad, hi + pad, 500)
                    fig, ax = plt.subplots(figsize=(7, 3.6))
                    ax.plot(xs, f(xs), color="#1f5fa8", label="f(x)")
                    ax.axhline(0, color="gray", lw=0.8)
                    ax.scatter([r], [0], color="red", zorder=3, label="raíz aproximada")
                    ax.set_xlabel("x"); ax.set_ylabel("f(x)"); ax.grid(alpha=0.3); ax.legend()
                    mostrar(fig)
                    if mostrar_res:
                        st.markdown("#### Resolución resumida")
                        lista(pasos())
                    st.caption("Tabla de iteraciones")
                    tabla(pd.DataFrame(filas, columns=cols).astype({"k": int}), "{:.10g}")
