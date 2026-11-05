"""
preguntas.py
Contenido y generadores de ejercicios de "Bit Quest" (SISTEMAS 4 y 6):
bytes, octal/hexadecimal, colores #RRGGBB y permisos de Linux (chmod).
No hace falta tocar app.py para añadir preguntas.
"""
import random
import re

PESOS = [128, 64, 32, 16, 8, 4, 2, 1]
HEXD = "0123456789ABCDEF"


# ---------------------------------------------------------------------------
# Utilidades de conversión
# ---------------------------------------------------------------------------
def bin8(n):
    return format(n, "08b")


def hex2(n):
    return format(n, "02X")


def pesos_encendidos(n):
    return [p for p in PESOS if n & p]


def suma_pesos(n):
    on = pesos_encendidos(n)
    return " + ".join(map(str, on)) if on else "0"


def rwx(digito):
    return ("r" if digito & 4 else "-") + ("w" if digito & 2 else "-") + ("x" if digito & 1 else "-")


def rwx_completo(num):
    return "".join(rwx(int(c)) for c in num)


def suma_llaves(digito):
    partes = [str(v) for v in (4, 2, 1) if digito & v]
    return " + ".join(partes) if partes else "0"


def explicar_chmod(num):
    nombres = ["Usuario", "Grupo", "Otros"]
    partes = [f"{nombres[i]} **{c}** = {suma_llaves(int(c))} = `{rwx(int(c))}`" for i, c in enumerate(num)]
    return " · ".join(partes) + f" → `{rwx_completo(num)}`"


def rgb_de_hex(codigo):
    c = codigo.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def hex_de_rgb(r, g, b):
    return f"#{hex2(r)}{hex2(g)}{hex2(b)}"


def comprobar(item, texto):
    """Comprueba una respuesta escrita (o elegida) contra un ejercicio."""
    t = (texto or "").strip()
    if not t:
        return False
    tipo = item["tipo"]
    if tipo == "numero":
        base = item["base"]
        t = re.sub(r"[\s|_]", "", t.lower())
        for pref in {2: ("0b",), 8: ("0o",), 16: ("0x", "#")}.get(base, ()):
            if t.startswith(pref):
                t = t[len(pref):]
                break
        try:
            return int(t, base) == item["valor"]
        except ValueError:
            return False
    if tipo == "lista":
        return [int(x) for x in re.findall(r"\d+", t)] == item["valor"]
    t = t.lower().replace(" ", "").lstrip("#")
    return t in [a.lower().lstrip("#") for a in item["aceptadas"]]


def _item(enunciado, tipo, canonica, explicacion, pista="", valor=None, base=None,
          aceptadas=None, opciones=None, color=None, placeholder="Escribe tu respuesta…", etiqueta=None):
    return {
        "enunciado": enunciado, "tipo": tipo, "canonica": canonica,
        "explicacion": explicacion, "pista": pista, "valor": valor, "base": base,
        "aceptadas": aceptadas or [], "opciones": opciones, "color": color,
        "placeholder": placeholder, "etiqueta": etiqueta,
    }


# ---------------------------------------------------------------------------
# Entrenador de bases (se generan al azar)
# ---------------------------------------------------------------------------
def g_dec2bin(n):
    return _item(f"Pasa el **{n}** a binario (8 bombillas).", "numero", bin8(n),
                 f"{n} = {suma_pesos(n)} → encendidas esas bombillas → **{bin8(n)}**.",
                 "Suma los pesos 128, 64, 32, 16, 8, 4, 2, 1 que necesites.",
                 valor=n, base=2, placeholder="p. ej. 10110010")


def g_bin2dec(n):
    return _item(f"¿Qué número decimal es **{bin8(n)}**?", "numero", str(n),
                 f"{suma_pesos(n)} = **{n}**.",
                 "Suma los pesos de las bombillas encendidas.", valor=n, base=10,
                 placeholder="p. ej. 178")


def g_bin2oct(n):
    pad = "0" + bin8(n)
    gr = [pad[0:3], pad[3:6], pad[6:9]]
    dig = [str(int(g, 2)) for g in gr]
    return _item(f"Pasa **{bin8(n)}** a octal (grupos de 3).", "numero", format(n, "o"),
                 f"Añade un 0 delante para completar grupos de 3: {' | '.join(gr)} → "
                 f"{' | '.join(dig)} → **{format(n, 'o')}**.",
                 "Agrupa de 3 en 3 desde la derecha; cada grupo vale de 0 a 7.",
                 valor=n, base=8, placeholder="p. ej. 377")


def g_bin2hex(n):
    b = bin8(n)
    gr = [b[:4], b[4:]]
    return _item(f"Pasa **{b}** a hexadecimal (grupos de 4).", "numero", hex2(n),
                 f"{gr[0]} | {gr[1]} → {HEXD[n >> 4]} | {HEXD[n & 15]} → **{hex2(n)}**.",
                 "Dos cachitos de 4 bits; del 10 al 15 se usan las letras A-F.",
                 valor=n, base=16, placeholder="p. ej. B2")


def g_dec2hex(n):
    return _item(f"Pasa el **{n}** a hexadecimal.", "numero", hex2(n),
                 f"{n} : 16 = **{n // 16}** y sobran **{n % 16}** → {HEXD[n // 16]} y {HEXD[n % 16]} → "
                 f"**{hex2(n)}**. (10=A, 11=B, 12=C, 13=D, 14=E, 15=F)",
                 "Divide entre 16: el cociente es la 1ª cifra y lo que sobra, la 2ª.",
                 valor=n, base=16, placeholder="p. ej. 2E")


def g_hex2dec(n):
    h = hex2(n)
    a, b = n >> 4, n & 15
    return _item(f"Pasa **{h}** a decimal.", "numero", str(n),
                 f"{h[0]} = {a} → {a}×16 = {a * 16}; {h[1]} = {b}. Total: {a * 16} + {b} = **{n}**.",
                 "Multiplica la 1ª cifra por 16 y suma la 2ª.", valor=n, base=10, placeholder="p. ej. 178")


def g_hex2bin(n):
    h = hex2(n)
    return _item(f"Pasa **{h}** a binario (8 bits).", "numero", bin8(n),
                 f"{h[0]} = {format(n >> 4, '04b')} | {h[1]} = {format(n & 15, '04b')} → **{bin8(n)}**.",
                 "Cada cifra hexadecimal son 4 bombillas.", valor=n, base=2, placeholder="p. ej. 10110010")


TIPOS_ENTRENADOR = {
    "Decimal → binario": [g_dec2bin],
    "Binario → decimal": [g_bin2dec],
    "Binario → octal": [g_bin2oct],
    "Binario → hexadecimal": [g_bin2hex],
    "Decimal → hexadecimal": [g_dec2hex],
    "Hexadecimal → decimal": [g_hex2dec],
    "Hexadecimal → binario": [g_hex2bin],
}
TIPOS_ENTRENADOR = {"Mezcla de todos": [f for fs in TIPOS_ENTRENADOR.values() for f in fs], **TIPOS_ENTRENADOR}
NIVELES_ENT = ["Fácil (0-63)", "Normal (0-255)"]


def generar_entrenador(tipo, nivel, cantidad=10):
    maximo = 63 if nivel.startswith("Fácil") else 255
    funcs = TIPOS_ENTRENADOR[tipo]
    numeros = random.sample(range(maximo + 1), cantidad)
    return [random.choice(funcs)(n) for n in numeros]


def generar_objetivos_bombillas(nivel, cantidad=8):
    maximo = 63 if nivel.startswith("Fácil") else 255
    return random.sample(range(1, maximo + 1), cantidad)


# ---------------------------------------------------------------------------
# Colores #RRGGBB
# ---------------------------------------------------------------------------
NOMBRES_COLOR = {
    "rojo": "#FF0000", "verde": "#00FF00", "azul": "#0000FF", "blanco": "#FFFFFF",
    "negro": "#000000", "amarillo": "#FFFF00", "cian": "#00FFFF", "magenta": "#FF00FF",
    "naranja": "#FF8000", "gris": "#808080",
}
# Ejercicio 32 de los PDF
PDF_COLORES = [("naranja", 255, 128, 0), ("verde", 46, 204, 113), ("azul oscuro", 18, 52, 86)]


def _pasos_hex(r, g, b):
    def paso(letra, c):
        return f"{letra} {c}: {c} : 16 = {c // 16}, sobran {c % 16} → {hex2(c)}"
    return " · ".join([paso("R", r), paso("G", g), paso("B", b)])


def g_rgb2hex(r, g, b, nombre=None):
    codigo = hex_de_rgb(r, g, b)
    pre = f"**Color {nombre}.** " if nombre else ""
    return _item(f"{pre}Convierte cada luz a hexadecimal y escribe el código **#RRGGBB**: "
                 f"R = {r}, G = {g}, B = {b}.", "texto", codigo,
                 f"{_pasos_hex(r, g, b)} → **{codigo}**.",
                 "Divide cada número entre 16: cociente = 1ª cifra, resto = 2ª. 255 = FF, 0 = 00.",
                 aceptadas=[codigo], color=codigo, placeholder="p. ej. #FF8000")


def g_hex2rgb(codigo):
    r, g, b = rgb_de_hex(codigo)
    return _item(f"¿Qué valores decimales (R, G, B) tiene **{codigo}**?", "lista", f"{r}, {g}, {b}",
                 f"{codigo[1:3]} = {r} · {codigo[3:5]} = {g} · {codigo[5:7]} = {b} "
                 f"(1ª cifra ×16 + 2ª cifra).",
                 "Separa el código en 3 parejas: una por luz.", valor=[r, g, b], color=codigo,
                 placeholder="p. ej. 46, 204, 113")


def g_hex2nombre(nombre):
    codigo = NOMBRES_COLOR[nombre]
    r, g, b = rgb_de_hex(codigo)
    otros = random.sample([n for n in NOMBRES_COLOR if n != nombre], 3)
    ops = otros + [nombre]
    random.shuffle(ops)
    return _item(f"¿Qué color es **{codigo}**?", "texto", nombre,
                 f"{codigo}: R = {r}, G = {g}, B = {b} → **{nombre}**.",
                 "Mira qué luces están a tope (FF) y cuáles apagadas (00).",
                 aceptadas=[nombre], opciones=ops, color=codigo)


def g_nombre2hex(nombre):
    codigo = NOMBRES_COLOR[nombre]
    otros = random.sample([c for n, c in NOMBRES_COLOR.items() if n != nombre], 3)
    ops = otros + [codigo]
    random.shuffle(ops)
    r, g, b = rgb_de_hex(codigo)
    return _item(f"¿Cuál es el código del color **{nombre}**?", "texto", codigo,
                 f"{nombre} = R {r}, G {g}, B {b} → **{codigo}**.",
                 "Piensa qué luces hay que encender para ese color.",
                 aceptadas=[codigo], opciones=ops, color=codigo)


NIVELES_COLOR = ["Fácil (valores redondos)", "Normal (cualquier valor)"]


def generar_color(nivel, cantidad=10):
    items = [g_rgb2hex(r, g, b, n) for n, r, g, b in PDF_COLORES]
    comp = [0, 64, 128, 192, 255] if nivel.startswith("Fácil") else list(range(256))
    for i in range(cantidad - len(items)):
        tipo = i % 4
        if tipo == 0:
            items.append(g_rgb2hex(random.choice(comp), random.choice(comp), random.choice(comp)))
        elif tipo == 1:
            items.append(g_hex2rgb(hex_de_rgb(random.choice(comp), random.choice(comp), random.choice(comp))))
        elif tipo == 2:
            items.append(g_hex2nombre(random.choice(list(NOMBRES_COLOR))))
        else:
            items.append(g_nombre2hex(random.choice(list(NOMBRES_COLOR))))
    random.shuffle(items)
    return items


# ---------------------------------------------------------------------------
# Permisos de Linux (chmod)
# ---------------------------------------------------------------------------
CASOS_CHMOD = [
    ("El dueño lo puede hacer todo; el grupo y los demás solo pueden ver y ejecutar.", "755"),
    ("Solo el dueño puede leer y escribir; el grupo y los demás no pueden hacer nada.", "600"),
    ("El dueño puede leer y escribir; el grupo solo leer; los demás nada.", "640"),
    ("Todos pueden leer; solo el dueño puede escribir.", "644"),
    ("Solo el dueño puede hacer de todo; nadie más tiene ningún permiso.", "700"),
    ("Todo el mundo puede hacerlo todo (¡peligroso!).", "777"),
    ("El dueño puede leer y ejecutar; el grupo solo leer; los demás nada.", "540"),
    ("El dueño y el grupo pueden leer y escribir; los demás solo leer.", "664"),
    ("Nadie puede escribir ni ejecutar: todos solo pueden leer.", "444"),
    ("El dueño lo puede todo, el grupo lee y ejecuta, los demás nada.", "750"),
]
COMUNES = ["755", "644", "700", "600", "640", "750", "777", "664", "444", "555", "711", "400", "660", "775", "500"]


def g_num2rwx(num):
    return _item(f"¿Qué permisos da `chmod {num} fichero`? Escríbelos como `rwxrwxrwx`.", "texto",
                 rwx_completo(num), explicar_chmod(num),
                 "Cada dígito es la suma de las llaves: r = 4, w = 2, x = 1.",
                 aceptadas=[rwx_completo(num)], placeholder="p. ej. rwxr-xr-x")


def g_rwx2num(num):
    return _item(f"¿Qué número `chmod` corresponde a **{rwx_completo(num)}**?", "texto", num,
                 explicar_chmod(num), "Separa en 3 grupos de 3 letras y suma las llaves de cada uno.",
                 aceptadas=[num], placeholder="p. ej. 755")


def g_digito(d):
    ops = {rwx(d)}
    while len(ops) < 4:
        ops.add(rwx(random.randint(0, 7)))
    ops = list(ops)
    random.shuffle(ops)
    return _item(f"¿Qué permisos da el dígito **{d}**?", "texto", rwx(d),
                 f"{d} = {suma_llaves(d)} = `{rwx(d)}`.", "Descompón en 4 + 2 + 1.",
                 aceptadas=[rwx(d)], opciones=ops)


def g_desc2num(desc, num):
    return _item(f"{desc}\n\n¿Qué número `chmod` usarías?", "texto", num, explicar_chmod(num),
                 "Usuario, grupo, otros: un dígito para cada uno.", aceptadas=[num], placeholder="p. ej. 755")


def generar_chmod(cantidad=10):
    items = []
    for n in random.sample(COMUNES, 3):
        items.append(g_num2rwx(n))
    for n in random.sample(COMUNES, 3):
        items.append(g_rwx2num(n))
    for d in random.sample(range(8), 2):
        items.append(g_digito(d))
    for desc, num in random.sample(CASOS_CHMOD, 2):
        items.append(g_desc2num(desc, num))
    random.shuffle(items)
    return items[:cantidad]


# ---------------------------------------------------------------------------
# ¿Te atreves? (los 3 retos del PDF + 4 extra)
# ---------------------------------------------------------------------------
def reto_final():
    return [
        _item("🎯 **(Del PDF)** ¿Qué color es **#00FF00**?", "texto", "verde",
              "#00FF00: R = 00, G = FF, B = 00 → solo la luz verde está a tope → **verde**.",
              "Mira qué luz está al máximo (FF).", aceptadas=["verde", "green", "verde puro"],
              color="#00FF00", placeholder="Escribe el color"),
        _item("🎯 **(Del PDF)** Pasa el **200** a hexadecimal.", "numero", "C8",
              "200 : 16 = 12 (C) y sobran 8 → **C8**.",
              "Divide entre 16 · 12 = C.", valor=200, base=16, placeholder="p. ej. 2E"),
        _item("🎯 **(Del PDF)** ¿Qué permisos da `chmod 700`? Escríbelos como `rwxrwxrwx`.", "texto", "rwx------",
              explicar_chmod("700"), "Suma las llaves (4, 2, 1).", aceptadas=["rwx------"],
              placeholder="p. ej. rwxr-xr-x"),
        _item("🔥 **Extra:** Pasa el **175** a hexadecimal.", "numero", "AF",
              "175 : 16 = 10 (A) y sobran 15 (F) → **AF**.", "10 = A y 15 = F.", valor=175, base=16,
              placeholder="p. ej. 2E"),
        _item("🔥 **Extra:** ¿Qué código tiene el color con R = 0, G = 255, B = 255?", "texto", "#00FFFF",
              "R 0 → 00 · G 255 → FF · B 255 → FF → **#00FFFF** (cian).", "255 en hexadecimal es FF.",
              aceptadas=["#00FFFF"], color="#00FFFF", placeholder="p. ej. #FF8000"),
        _item("🔥 **Extra:** ¿Qué permisos da `chmod 640`? Escríbelos como `rwxrwxrwx`.", "texto", "rw-r-----",
              explicar_chmod("640"), "6 = 4 + 2 · 4 = solo leer · 0 = nada.", aceptadas=["rw-r-----"],
              placeholder="p. ej. rwxr-xr-x"),
        _item("🔥 **Extra:** Pasa **11001000** a decimal.", "numero", "200",
              "128 + 64 + 8 = **200**.", "Suma los pesos de las bombillas encendidas.", valor=200, base=10,
              placeholder="p. ej. 178"),
    ]


# ---------------------------------------------------------------------------
# Verdadero o falso
# ---------------------------------------------------------------------------
VERDADERO_FALSO = [
    ("Un byte son 8 bits (8 bombillas), cada una apagada (0) o encendida (1).", True,
     "Con 8 bombillas se pueden formar 256 valores distintos: del 0 al 255."),
    ("Con las 8 bombillas encendidas el número es 255.", True, "128+64+32+16+8+4+2+1 = 255."),
    ("Cada bombilla vale el doble que la de su derecha.", True, "1, 2, 4, 8, 16, 32, 64, 128."),
    ("255 en octal es 377.", True, "011 | 111 | 111 → 3 | 7 | 7."),
    ("255 en hexadecimal es FF.", True, "1111 | 1111 → F | F."),
    ("Para pasar de binario a octal se agrupan los bits de 4 en 4.", False,
     "En octal se agrupa de 3 en 3; de 4 en 4 es para el hexadecimal."),
    ("Para pasar de binario a hexadecimal se agrupan los bits de 4 en 4.", True, "Cada grupo de 4 bits da una cifra 0-9 o A-F."),
    ("El sistema octal usa los dígitos del 0 al 8.", False, "Usa del 0 al 7 (8 dígitos en total)."),
    ("En hexadecimal, la letra E vale 14.", True, "10=A, 11=B, 12=C, 13=D, 14=E, 15=F."),
    ("En hexadecimal, la letra F vale 16.", False, "F vale 15; el 16 se escribe 10."),
    ("111 en binario es el 7 en octal.", True, "4 + 2 + 1 = 7."),
    ("Al pasar un byte a octal se añade un 0 delante para completar grupos de 3.", True,
     "8 bits no son múltiplo de 3: 0 11 | 111 | 111 → 011 | 111 | 111."),
    ("Cada luz de la pantalla (rojo, verde y azul) va de 0 a 255.", True, "0 = luz apagada, 255 = luz a tope (1 byte por luz)."),
    ("#FFFFFF es el color negro.", False, "#FFFFFF es blanco (todas las luces a tope); el negro es #000000."),
    ("#FF0000 es el color rojo.", True, "Solo la luz roja a tope."),
    ("#FFFF00 es amarillo: rojo + verde a tope.", True, "Y el azul apagado."),
    ("Cada luz usa dos cifras hexadecimales porque el máximo, 255, en hexadecimal es FF.", True,
     "Por eso el código es #RRGGBB."),
    ("46 en hexadecimal es 2E.", True, "46 : 16 = 2 y sobran 14 (E)."),
    ("200 en hexadecimal es C8.", True, "200 : 16 = 12 (C) y sobran 8."),
    ("En Linux, r vale 4, w vale 2 y x vale 1.", True, "r = leer, w = escribir, x = ejecutar."),
    ("El permiso 4 significa «escribir».", False, "El 4 es leer (r); escribir vale 2."),
    ("`chmod 755` da los permisos rwxr-xr-x.", True, "7 = rwx, 5 = r-x, 5 = r-x."),
    ("Con `chmod 755`, el grupo puede modificar el fichero.", False, "El grupo tiene r-x: puede ver y usar, no cambiar."),
    ("«Otros» son todos los usuarios que no son el dueño ni del grupo.", True, "Usuario = dueño · Grupo = tu equipo · Otros = todos los demás."),
    ("`chmod 700` da todos los permisos al dueño y ninguno a los demás.", True, "rwx------."),
    ("El 6 en un permiso equivale a rw-.", True, "4 + 2 = 6."),
]


# ---------------------------------------------------------------------------
# Quiz de teoría. La correcta se escribe primero; el juego baraja las opciones.
# ---------------------------------------------------------------------------
BLOQUES = ["Bytes y bases", "Colores", "Permisos en Linux"]


def _q(bloque, enunciado, correcta, incorrectas, explicacion):
    return {"bloque": bloque, "enunciado": enunciado, "opciones": [correcta] + list(incorrectas),
            "correcta": 0, "explicacion": explicacion}


QUIZ = [
    _q(BLOQUES[0], "¿Cuánto vale la bombilla de más a la izquierda de un byte?", "128", ["8", "64", "256"],
       "Los pesos son 128, 64, 32, 16, 8, 4, 2, 1."),
    _q(BLOQUES[0], "¿Cuántos valores distintos puede representar un byte?", "256 (del 0 al 255)", ["255", "128", "8"],
       "2⁸ = 256 combinaciones: del 0 al 255."),
    _q(BLOQUES[0], "¿Qué dígitos usa el sistema octal?", "Del 0 al 7", ["Del 0 al 8", "Del 0 al 9", "Del 0 al F"],
       "Octal = base 8: ocho dígitos."),
    _q(BLOQUES[0], "¿Cuántos bits se agrupan para pasar a hexadecimal?", "4", ["3", "2", "8"],
       "Cada grupo de 4 bits da una cifra hexadecimal."),
    _q(BLOQUES[0], "¿Cuántos bits se agrupan para pasar a octal?", "3", ["4", "2", "8"],
       "Cada grupo de 3 bits da un dígito octal (0-7)."),
    _q(BLOQUES[0], "¿Cuánto vale 1111 en hexadecimal?", "F", ["E", "A", "9"], "8 + 4 + 2 + 1 = 15 = F."),
    _q(BLOQUES[0], "¿Cómo se escribe 255 en octal?", "377", ["255", "FF", "400"], "011 | 111 | 111 → 3 | 7 | 7."),
    _q(BLOQUES[0], "¿Cuánto es 46 en hexadecimal?", "2E", ["3E", "2D", "46"], "46 : 16 = 2 y sobran 14 (E)."),
    _q(BLOQUES[0], "¿Qué letra representa el 12 en hexadecimal?", "C", ["A", "D", "F"], "10=A, 11=B, 12=C, 13=D, 14=E, 15=F."),
    _q(BLOQUES[0], "¿Cuánto es 11001000 en decimal?", "200", ["190", "208", "212"], "128 + 64 + 8 = 200."),
    _q(BLOQUES[0], "¿Por qué se añade un 0 delante al pasar un byte a octal?",
       "Para completar grupos de 3 bits (8 bits no es múltiplo de 3)", ["Porque el 0 es obligatorio en octal", "Para que valga el doble", "Para pasar a hexadecimal"],
       "0 11 | 111 | 111 → 011 | 111 | 111."),
    _q(BLOQUES[1], "¿Cuántas luces mezcla cada píxel de la pantalla?", "3 (rojo, verde y azul)", ["2", "4", "8"],
       "Mezclándolas sale cualquier color."),
    _q(BLOQUES[1], "¿Qué valor es «luz a tope»?", "255", ["100", "128", "256"], "0 = apagada, 255 = máximo (1 byte por luz)."),
    _q(BLOQUES[1], "¿Qué significa #RRGGBB?", "Dos cifras hexadecimales para rojo, verde y azul", ["Tres números decimales", "Un color en octal", "El nombre del color"],
       "Dos cifras por luz porque el máximo, 255, en hexadecimal es FF."),
    _q(BLOQUES[1], "¿Qué color es #FF8000?", "Naranja", ["Verde", "Azul oscuro", "Gris"], "Rojo a tope, verde a la mitad (80), azul apagado."),
    _q(BLOQUES[1], "¿Cuál es el código del verde «puro»?", "#00FF00", ["#FF0000", "#0000FF", "#FFFFFF"], "Solo la luz verde a tope."),
    _q(BLOQUES[1], "¿Qué dos luces se mezclan para obtener amarillo?", "Rojo y verde", ["Rojo y azul", "Verde y azul", "Solo el rojo"], "#FFFF00."),
    _q(BLOQUES[1], "¿Cuánto es 128 en hexadecimal?", "80", ["FF", "08", "1F"], "128 : 16 = 8 y sobra 0."),
    _q(BLOQUES[1], "¿Cuánto es 204 en hexadecimal?", "CC", ["C4", "DD", "CA"], "204 : 16 = 12 (C) y sobran 12 (C)."),
    _q(BLOQUES[1], "¿Qué color es #123456?", "Azul oscuro", ["Naranja", "Verde", "Blanco"], "18, 52, 86: valores bajos con más azul."),
    _q(BLOQUES[2], "¿Qué tres tipos de personas tiene cada permiso?", "Usuario, grupo y otros", ["Root, admin y guest", "Lectura, escritura y ejecución", "Dueño, jefe y empleado"],
       "Usuario = el dueño · Grupo = tu equipo · Otros = todos los demás."),
    _q(BLOQUES[2], "¿Cuánto vale el permiso de escribir (w)?", "2", ["1", "4", "7"], "r = 4, w = 2, x = 1."),
    _q(BLOQUES[2], "¿Qué permiso da el 5?", "r-x", ["rw-", "-wx", "r--"], "4 + 1 = leer + ejecutar."),
    _q(BLOQUES[2], "¿Qué permisos da el 6?", "rw-", ["r-x", "rwx", "-wx"], "4 + 2 = leer + escribir."),
    _q(BLOQUES[2], "¿Qué permisos da chmod 755?", "rwxr-xr-x", ["rwxrwxrwx", "rw-r--r--", "rwx------"], "7 = rwx, 5 = r-x, 5 = r-x."),
    _q(BLOQUES[2], "¿Qué permisos da chmod 644?", "rw-r--r--", ["rwxr-xr-x", "rw-rw-rw-", "r--r--r--"], "6 = rw-, 4 = r--, 4 = r--."),
    _q(BLOQUES[2], "¿Qué chmod deja todo al dueño y nada al resto?", "700", ["777", "007", "755"], "rwx------."),
    _q(BLOQUES[2], "¿Qué permite la «x»?", "Ejecutar", ["Leer", "Escribir", "Borrar el usuario"], "x = ejecutar (vale 1)."),
]


# ---------------------------------------------------------------------------
# Chuleta
# ---------------------------------------------------------------------------
CHULETA = """
### 💡 Un byte = 8 bombillas

| 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

Cada bombilla vale el doble que la de su derecha. Todas encendidas: **255**.

### 🔄 Otras bases

- **Octal** (0-7): grupos de **3** bits. `0 11 | 111 | 111` → `3 | 7 | 7` → **377**
- **Hexadecimal** (0-9 y A-F): grupos de **4** bits. `1111 | 1111` → `F | F` → **FF**
- 255₁₀ = 377₈ = FF₁₆

| 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|
| A | B | C | D | E | F |

**Truco: divide entre 16.** El cociente es la 1ª cifra; lo que sobra, la 2ª.
Ej.: 46 : 16 = 2 y sobran 14 → **2E**. Ej.: 200 : 16 = 12 (C), sobran 8 → **C8**.

### 🎨 Colores `#RRGGBB`

Tres luces (Rojo, Verde, Azul), cada una de 0 a 255 (= 00 a FF).

| Color | Código |
|---|---|
| rojo | #FF0000 |
| verde | #00FF00 |
| azul | #0000FF |
| blanco | #FFFFFF |
| negro | #000000 |
| amarillo | #FFFF00 |
| naranja | #FF8000 |

### 🐧 Permisos en Linux

`r` leer = **4** · `w` escribir = **2** · `x` ejecutar = **1**

Tres tipos de personas: **Usuario** (dueño) · **Grupo** · **Otros**.
Se suman las llaves de cada uno:

| Dígito | Suma | Permisos |
|---|---|---|
| 7 | 4+2+1 | rwx |
| 6 | 4+2 | rw- |
| 5 | 4+1 | r-x |
| 4 | 4 | r-- |
| 0 | 0 | --- |

`chmod 755 fichero` → `rwxr-xr-x`
"""
