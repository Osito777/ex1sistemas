"""
Bit Quest 💡 · Juego interactivo sobre bytes, octal/hexadecimal, colores #RRGGBB y permisos chmod.
Ejecutar con:  streamlit run app.py
"""
import random
import re

import streamlit as st

from preguntas import (
    BLOQUES, CASOS_CHMOD, CHULETA, NIVELES_COLOR, NIVELES_ENT, PESOS, QUIZ,
    TIPOS_ENTRENADOR, VERDADERO_FALSO, bin8, comprobar, explicar_chmod,
    generar_chmod, generar_color, generar_entrenador, generar_objetivos_bombillas,
    hex2, hex_de_rgb, reto_final, rgb_de_hex, rwx_completo,
)

st.set_page_config(page_title="Bit Quest", page_icon="💡", layout="centered")

# ---------------------------------------------------------------------------
# Configuración del juego
# ---------------------------------------------------------------------------
PUNTOS_PREGUNTA = 5

NIVELES = [
    (0, "Bit 🔹"),
    (30, "Byte 💡"),
    (80, "Hexadecimal 🔷"),
    (150, "Administrador de sistemas 🐧"),
    (250, "Root 👑"),
]

MODOS = [
    "🏠 Inicio",
    "💡 Enciende las bombillas",
    "🔄 Entrenador de bases",
    "🎨 Retos de color",
    "🔐 Traduce permisos",
    "🛠️ Construye el permiso",
    "✅ Verdadero o falso",
    "🧠 Quiz de teoría",
    "🎯 ¿Te atreves?",
    "🧪 Laboratorio",
    "📖 Chuleta",
]

VF_ITEMS = [
    {"enunciado": txt, "opciones": ["Verdadero", "Falso"], "correcta": 0 if ok else 1,
     "explicacion": expl, "barajar": False}
    for txt, ok, expl in VERDADERO_FALSO
]
BLOQUE_ID = {"Todos los bloques": "q0", **{b: f"q{i + 1}" for i, b in enumerate(BLOQUES)}}

QUIENES = ["Usuario (el dueño)", "Grupo (tu equipo)", "Otros (todos los demás)"]
PERMS = {"r · leer (4)": 4, "w · escribir (2)": 2, "x · ejecutar (1)": 1}


# ---------------------------------------------------------------------------
# Estado y puntuación
# ---------------------------------------------------------------------------
def iniciar_estado():
    for clave, valor in {"puntos": 0, "racha": 0, "mejor_racha": 0,
                         "aciertos": 0, "intentos": 0}.items():
        st.session_state.setdefault(clave, valor)


def nivel_actual():
    nombre = NIVELES[0][1]
    for minimo, titulo in NIVELES:
        if st.session_state.puntos >= minimo:
            nombre = titulo
    return nombre


def siguiente_nivel():
    for minimo, titulo in NIVELES:
        if st.session_state.puntos < minimo:
            return minimo, titulo
    return None


def registrar(aciertos, intentos, puntos, perfecto):
    s = st.session_state
    s.aciertos += aciertos
    s.intentos += intentos
    s.puntos += puntos
    if perfecto:
        s.racha += 1
        s.mejor_racha = max(s.mejor_racha, s.racha)
    else:
        s.racha = 0


def reiniciar_modo(modo):
    for clave in [k for k in st.session_state if k.startswith(f"{modo}_")]:
        del st.session_state[clave]


def preparar_cola(modo, total, limite=None):
    """Crea (una sola vez) el orden aleatorio de preguntas de un modo."""
    if f"{modo}_orden" not in st.session_state:
        orden = list(range(total))
        random.shuffle(orden)
        st.session_state[f"{modo}_orden"] = orden[:limite] if limite else orden
        st.session_state[f"{modo}_pos"] = 0
        st.session_state[f"{modo}_res"] = None
        st.session_state[f"{modo}_ok"] = 0


def avanzar(modo):
    st.session_state[f"{modo}_pos"] += 1
    st.session_state[f"{modo}_res"] = None


def pantalla_final(modo, titulo):
    orden = st.session_state[f"{modo}_orden"]
    ok = st.session_state[f"{modo}_ok"]
    total = len(orden)
    st.success(f"🏁 ¡Completado! Has acertado **{ok} de {total}** en «{titulo}».")
    if ok / total >= 0.8:
        st.balloons()
        st.write("Nota: **Sobresaliente** 🎉")
    elif ok / total >= 0.5:
        st.write("Nota: **Aprobado**, ¡pero puedes mejorarlo! 💪")
    else:
        st.write("Nota: **A repasar** la chuleta 📖 y volver a intentarlo.")
    st.button("🔁 Jugar otra vez", on_click=reiniciar_modo, args=(modo,), key=f"again_{modo}")


# ---------------------------------------------------------------------------
# Elementos visuales reutilizables
# ---------------------------------------------------------------------------
def hex_valido(texto):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", texto or ""))


def muestra_color(codigo, alto=80):
    if hex_valido(codigo):  # solo se pinta si es un código válido (evita HTML inesperado)
        st.markdown(
            f"<div style='background:{codigo};height:{alto}px;border-radius:12px;"
            f"border:1px solid rgba(128,128,128,.5)'></div>",
            unsafe_allow_html=True,
        )


def fila_bombillas(encendidas):
    celdas = "".join(
        f"<div style='text-align:center;flex:1'><div style='font-size:1.7rem'>{'💡' if p in encendidas else '⚫'}</div>"
        f"<div style='font-size:.8rem;opacity:.7'>{p}</div></div>"
        for p in PESOS
    )
    st.markdown(f"<div style='display:flex;gap:2px'>{celdas}</div>", unsafe_allow_html=True)


def selector_bombillas(clave):
    sel = st.pills("Bombillas encendidas (toca las que quieras encender)", PESOS,
                   selection_mode="multi", key=clave) or []
    fila_bombillas(sel)
    return sel


def grid_permisos(prefijo):
    """Tres filas de pastillas (usuario/grupo/otros). Devuelve el número chmod, p. ej. '755'."""
    digitos = []
    for i, quien in enumerate(QUIENES):
        sel = st.pills(quien, list(PERMS), selection_mode="multi", key=f"{prefijo}_{i}") or []
        digitos.append(sum(PERMS[s] for s in sel))
    return "".join(map(str, digitos))


# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
def barra_lateral():
    s = st.session_state
    st.sidebar.title("💡 Bit Quest")
    modo = st.sidebar.radio("Elige modo de juego", MODOS, key="modo_menu")
    st.sidebar.divider()
    st.sidebar.metric("Puntos", s.puntos)
    c1, c2 = st.sidebar.columns(2)
    c1.metric("Racha 🔥", s.racha)
    c2.metric("Mejor racha", s.mejor_racha)
    precision = (s.aciertos / s.intentos * 100) if s.intentos else 0
    st.sidebar.write(f"**Nivel:** {nivel_actual()}")
    st.sidebar.write(f"**Precisión:** {precision:.0f}% ({s.aciertos}/{s.intentos})")
    prox = siguiente_nivel()
    if prox:
        minimo, titulo = prox
        st.sidebar.progress(min(s.puntos / minimo, 1.0))
        st.sidebar.caption(f"Te faltan {minimo - s.puntos} puntos para {titulo}")
    else:
        st.sidebar.caption("¡Nivel máximo alcanzado!")
    if st.sidebar.button("🗑️ Reiniciar todo"):
        st.session_state.clear()
        st.rerun()
    return modo


# ---------------------------------------------------------------------------
# Modo genérico: ejercicios con respuesta escrita (o elegida)
# ---------------------------------------------------------------------------
def modo_escrito(modo, titulo, descripcion, crear, selectores=None):
    st.header(titulo)
    st.caption(descripcion)
    if selectores:
        selectores()
    if f"{modo}_items" not in st.session_state:
        items = crear()
        st.session_state[f"{modo}_items"] = items
        st.session_state[f"{modo}_orden"] = list(range(len(items)))
        st.session_state[f"{modo}_pos"] = 0
        st.session_state[f"{modo}_res"] = None
        st.session_state[f"{modo}_ok"] = 0
    items = st.session_state[f"{modo}_items"]
    pos = st.session_state[f"{modo}_pos"]
    if pos >= len(items):
        pantalla_final(modo, titulo)
        return

    item = items[pos]
    st.progress(pos / len(items), text=f"Ejercicio {pos + 1} de {len(items)}")
    st.markdown(f"### {item['enunciado']}")

    res = st.session_state[f"{modo}_res"]
    if res is None:
        if item["pista"]:
            with st.expander("💡 Pista"):
                st.write(item["pista"])
        with st.form(f"form_{modo}_{pos}"):
            if item["opciones"]:
                resp = st.radio("Tu respuesta", item["opciones"], index=None, key=f"{modo}_in_{pos}")
            else:
                resp = st.text_input("Tu respuesta", key=f"{modo}_in_{pos}", placeholder=item["placeholder"])
            enviar = st.form_submit_button("Comprobar ✅", type="primary")
        if enviar:
            if not resp or not resp.strip():
                st.warning("Escribe o elige una respuesta primero.")
            else:
                ok = comprobar(item, resp)
                registrar(1 if ok else 0, 1, PUNTOS_PREGUNTA if ok else 0, ok)
                st.session_state[f"{modo}_ok"] += 1 if ok else 0
                st.session_state[f"{modo}_res"] = {"resp": resp, "ok": ok}
                st.rerun()
    else:
        if res["ok"]:
            st.success(f"✅ ¡Correcto! +{PUNTOS_PREGUNTA} puntos")
        else:
            st.error(f"❌ Has respondido «{res['resp']}». La correcta era: **{item['canonica']}**")
        st.info(item["explicacion"])
        if item["color"]:
            muestra_color(item["color"], 60)
        st.button("Siguiente ➡️", on_click=avanzar, args=(modo,), type="primary")


# ---------------------------------------------------------------------------
# Modo: enciende las bombillas
# ---------------------------------------------------------------------------
def modo_bombillas():
    modo = "bomb"
    st.header("💡 Enciende las bombillas")
    st.caption("Forma cada número encendiendo las bombillas necesarias (cada una vale el doble que la de su derecha).")
    st.selectbox("Dificultad", NIVELES_ENT, key="sel_bomb_nivel",
                 on_change=reiniciar_modo, args=(modo,))
    if f"{modo}_items" not in st.session_state:
        st.session_state[f"{modo}_items"] = generar_objetivos_bombillas(st.session_state["sel_bomb_nivel"])
        st.session_state[f"{modo}_orden"] = list(range(len(st.session_state[f"{modo}_items"])))
        st.session_state[f"{modo}_pos"] = 0
        st.session_state[f"{modo}_res"] = None
        st.session_state[f"{modo}_ok"] = 0
    items = st.session_state[f"{modo}_items"]
    pos = st.session_state[f"{modo}_pos"]
    if pos >= len(items):
        pantalla_final(modo, "Enciende las bombillas")
        return

    objetivo = items[pos]
    st.progress(pos / len(items), text=f"Número {pos + 1} de {len(items)}")
    st.markdown(f"### Forma el número **{objetivo}**")
    res = st.session_state[f"{modo}_res"]
    if res is None:
        sel = selector_bombillas(f"{modo}_sel_{pos}")
        st.write(f"Suma actual: **{sum(sel)}**")
        if st.button("Comprobar ✅", type="primary"):
            ok = sum(sel) == objetivo
            registrar(1 if ok else 0, 1, PUNTOS_PREGUNTA if ok else 0, ok)
            st.session_state[f"{modo}_ok"] += 1 if ok else 0
            st.session_state[f"{modo}_res"] = {"sel": list(sel), "ok": ok}
            st.rerun()
    else:
        fila_bombillas(res["sel"])
        if res["ok"]:
            st.success(f"✅ ¡Correcto! {objetivo} = {' + '.join(str(p) for p in PESOS if objetivo & p)} · +{PUNTOS_PREGUNTA} puntos")
        else:
            st.error(f"❌ Tu suma era {sum(res['sel'])}. {objetivo} = "
                     f"{' + '.join(str(p) for p in PESOS if objetivo & p)} → **{bin8(objetivo)}**")
        st.button("Siguiente ➡️", on_click=avanzar, args=(modo,), type="primary")


# ---------------------------------------------------------------------------
# Modo: construye el permiso
# ---------------------------------------------------------------------------
def modo_construye():
    modo = "con"
    st.header("🛠️ Construye el permiso")
    st.caption("Marca las llaves (r, w, x) de cada tipo de persona para cumplir lo que se pide.")
    preparar_cola(modo, len(CASOS_CHMOD))
    pos = st.session_state[f"{modo}_pos"]
    orden = st.session_state[f"{modo}_orden"]
    if pos >= len(orden):
        pantalla_final(modo, "Construye el permiso")
        return

    desc, objetivo = CASOS_CHMOD[orden[pos]]
    st.progress(pos / len(orden), text=f"Caso {pos + 1} de {len(orden)}")
    st.info(desc)
    res = st.session_state[f"{modo}_res"]
    if res is None:
        num = grid_permisos(f"{modo}_{pos}")
        st.write(f"Tu permiso: **`{num}`** → `{rwx_completo(num)}`")
        if st.button("Comprobar ✅", type="primary"):
            ok = num == objetivo
            registrar(1 if ok else 0, 1, PUNTOS_PREGUNTA if ok else 0, ok)
            st.session_state[f"{modo}_ok"] += 1 if ok else 0
            st.session_state[f"{modo}_res"] = {"num": num, "ok": ok}
            st.rerun()
    else:
        if res["ok"]:
            st.success(f"✅ ¡Correcto! `chmod {objetivo}` · +{PUNTOS_PREGUNTA} puntos")
        else:
            st.error(f"❌ Tu permiso era {res['num']} (`{rwx_completo(res['num'])}`). Lo correcto: **{objetivo}**")
        st.info(explicar_chmod(objetivo))
        st.button("Siguiente ➡️", on_click=avanzar, args=(modo,), type="primary")


# ---------------------------------------------------------------------------
# Modo genérico: opción múltiple (V/F, quiz)
# ---------------------------------------------------------------------------
def modo_opciones(modo, titulo, items, descripcion="", cabecera=True):
    if cabecera:
        st.header(titulo)
        if descripcion:
            st.caption(descripcion)
    if not items:
        st.info("No hay preguntas en este bloque.")
        return
    preparar_cola(modo, len(items))
    pos = st.session_state[f"{modo}_pos"]
    orden = st.session_state[f"{modo}_orden"]
    if pos >= len(orden):
        pantalla_final(modo, titulo)
        return

    idx = orden[pos]
    item = items[idx]
    st.progress(pos / len(orden), text=f"Pregunta {pos + 1} de {len(orden)}")
    st.markdown(f"### {item['enunciado']}")
    opciones = list(item["opciones"])
    texto_correcto = opciones[item["correcta"]]
    if item.get("barajar", True):
        random.Random(f"{modo}-{idx}").shuffle(opciones)

    res = st.session_state[f"{modo}_res"]
    if res is None:
        with st.form(f"form_{modo}_{pos}"):
            eleccion = st.radio("Tu respuesta", opciones, index=None, key=f"{modo}_radio_{pos}")
            enviar = st.form_submit_button("Comprobar ✅", type="primary")
        if enviar:
            if eleccion is None:
                st.warning("Elige una opción primero.")
            else:
                ok = eleccion == texto_correcto
                registrar(1 if ok else 0, 1, PUNTOS_PREGUNTA if ok else 0, ok)
                st.session_state[f"{modo}_ok"] += 1 if ok else 0
                st.session_state[f"{modo}_res"] = {"eleccion": eleccion, "ok": ok}
                st.rerun()
    else:
        if res["ok"]:
            st.success(f"✅ ¡Correcto! +{PUNTOS_PREGUNTA} puntos")
        else:
            st.error(f"❌ Has elegido «{res['eleccion']}». La correcta era: **{texto_correcto}**")
        st.info(item["explicacion"])
        st.button("Siguiente ➡️", on_click=avanzar, args=(modo,), type="primary")


def modo_quiz():
    st.header("🧠 Quiz de teoría")
    st.caption("Elige un bloque o juega con todos a la vez.")
    bloque = st.selectbox("Bloque", list(BLOQUE_ID), key="quiz_bloque")
    items = QUIZ if bloque == "Todos los bloques" else [q for q in QUIZ if q["bloque"] == bloque]
    modo_opciones(BLOQUE_ID[bloque], f"Quiz · {bloque}", items, cabecera=False)


# ---------------------------------------------------------------------------
# Selectores de los modos con ejercicios generados
# ---------------------------------------------------------------------------
def selectores_entrenador():
    c1, c2 = st.columns(2)
    c1.selectbox("Tipo de ejercicio", list(TIPOS_ENTRENADOR), key="sel_ent_tipo",
                 on_change=reiniciar_modo, args=("ent",))
    c2.selectbox("Dificultad", NIVELES_ENT, key="sel_ent_nivel",
                 on_change=reiniciar_modo, args=("ent",))


def selectores_color():
    st.selectbox("Dificultad", NIVELES_COLOR, key="sel_col_nivel",
                 on_change=reiniciar_modo, args=("col",))


# ---------------------------------------------------------------------------
# Laboratorio (sin puntos: para experimentar)
# ---------------------------------------------------------------------------
def lab_bombillas():
    sel = selector_bombillas("lab_bomb")
    n = sum(sel)
    b = bin8(n)
    pad = "0" + b
    st.markdown(f"**Decimal:** `{n}` · **Binario:** `{b}`")
    st.markdown(f"**Octal** (grupos de 3): `{pad[0:3]} | {pad[3:6]} | {pad[6:9]}` → `{format(n, 'o')}`")
    st.markdown(f"**Hexadecimal** (grupos de 4): `{b[:4]} | {b[4:]}` → `{hex2(n)}`")


def lab_color():
    c1, c2, c3 = st.columns(3)
    r = c1.slider("R · rojo", 0, 255, 255, key="lab_r")
    g = c2.slider("G · verde", 0, 255, 128, key="lab_g")
    b = c3.slider("B · azul", 0, 255, 0, key="lab_b")
    codigo = hex_de_rgb(r, g, b)
    muestra_color(codigo, 100)
    st.markdown(f"### `{codigo}`")
    st.caption(f"R {r} → {hex2(r)} · G {g} → {hex2(g)} · B {b} → {hex2(b)}")
    st.divider()
    escrito = st.text_input("…o escribe un código para verlo", value="#2ECC71", key="lab_hex")
    if hex_valido(escrito):
        muestra_color(escrito, 60)
        rr, gg, bb = rgb_de_hex(escrito)
        st.caption(f"{escrito.upper()} → R {rr}, G {gg}, B {bb}")
    else:
        st.caption("Formato: # seguido de 6 cifras hexadecimales (por ejemplo #FF8000).")


def lab_permisos():
    num = grid_permisos("lab_perm")
    st.markdown(f"### `chmod {num} fichero` → `{rwx_completo(num)}`")
    st.markdown(explicar_chmod(num))


def modo_laboratorio():
    st.header("🧪 Laboratorio")
    st.caption("Experimenta sin puntos: mira cómo cambian los números al tocar los controles.")
    herramienta = st.radio("Herramienta", ["💡 Bombillas", "🎨 Mezclador de color", "🔐 Permisos chmod"],
                           horizontal=True, key="sel_lab")
    if herramienta.startswith("💡"):
        lab_bombillas()
    elif herramienta.startswith("🎨"):
        lab_color()
    else:
        lab_permisos()


# ---------------------------------------------------------------------------
# Inicio
# ---------------------------------------------------------------------------
def pantalla_inicio():
    st.title("💡 Bit Quest")
    st.subheader("Bytes, hexadecimal, colores y permisos")
    st.write(
        "Practica **binario, octal y hexadecimal**, el código de color `#RRGGBB` y los permisos de "
        "Linux (`chmod`) con ejercicios que se generan al azar, para que nunca se acaben."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Tipos de ejercicio", len(TIPOS_ENTRENADOR) - 1 + 4)
    c2.metric("Verdadero o falso", len(VF_ITEMS))
    c3.metric("Preguntas de quiz", len(QUIZ))
    st.markdown(
        """
**Modos de juego**
- 💡 **Enciende las bombillas**: forma números con un byte.
- 🔄 **Entrenador de bases**: decimal, binario, octal y hexadecimal (¡con el truco de dividir entre 16!).
- 🎨 **Retos de color**: del RGB al código `#RRGGBB` y al revés.
- 🔐 **Traduce permisos** y 🛠️ **Construye el permiso**: `chmod` con las llaves 4, 2 y 1.
- ✅ **Verdadero o falso** y 🧠 **Quiz de teoría**.
- 🎯 **¿Te atreves?**: los retos finales de los PDF y algunos extra.
- 🧪 **Laboratorio**: toca las bombillas, mezcla colores y mira los permisos sin puntos.
        """
    )
    st.info("👈 Elige un modo en el menú de la izquierda para empezar.")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    iniciar_estado()
    modo = barra_lateral()
    if modo == MODOS[0]:
        pantalla_inicio()
    elif modo == MODOS[1]:
        modo_bombillas()
    elif modo == MODOS[2]:
        modo_escrito(
            "ent", "🔄 Entrenador de bases", "Escribe la conversión. Sirven mayúsculas, minúsculas y ceros delante.",
            lambda: generar_entrenador(st.session_state.get("sel_ent_tipo", "Mezcla de todos"),
                                       st.session_state.get("sel_ent_nivel", NIVELES_ENT[1])),
            selectores_entrenador)
    elif modo == MODOS[3]:
        modo_escrito(
            "col", "🎨 Retos de color", "Los 3 primeros colores son del ejercicio 32 de los PDF (mezclados con otros).",
            lambda: generar_color(st.session_state.get("sel_col_nivel", NIVELES_COLOR[0])),
            selectores_color)
    elif modo == MODOS[4]:
        modo_escrito("tra", "🔐 Traduce permisos", "Pasa de número a letras y al revés (r = 4, w = 2, x = 1).",
                     generar_chmod)
    elif modo == MODOS[5]:
        modo_construye()
    elif modo == MODOS[6]:
        modo_opciones("vf", "✅ Verdadero o falso", VF_ITEMS, descripcion="Cuidado con las trampas.")
    elif modo == MODOS[7]:
        modo_quiz()
    elif modo == MODOS[8]:
        modo_escrito("te", "🎯 ¿Te atreves?", "Los 3 retos finales de los PDF y 4 extra. ¡Sin pistas fáciles!", reto_final)
    elif modo == MODOS[9]:
        modo_laboratorio()
    else:
        st.header("📖 Chuleta")
        st.markdown(CHULETA)


main()
