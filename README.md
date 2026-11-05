# 💡 Bit Quest

Juego interactivo hecho con **Streamlit** para practicar **bytes, binario, octal y hexadecimal**,
el **código de color #RRGGBB** y los **permisos de Linux (chmod)**.

Basado en los materiales de Sistemas (ejercicios 32 y 33 y el reto «¿Te atreves?»).

## 🎮 Modos de juego

| Modo | Qué hace |
|---|---|
| 💡 Enciende las bombillas | Forma números con un byte tocando las bombillas (128, 64, … 1). |
| 🔄 Entrenador de bases | Ejercicios generados al azar: decimal ⇄ binario, binario → octal (grupos de 3), binario → hexadecimal (grupos de 4), decimal ⇄ hexadecimal. |
| 🎨 Retos de color | Del RGB al código `#RRGGBB` y al revés, con vista previa del color. Incluye los 3 colores del ejercicio 32. |
| 🔐 Traduce permisos | `chmod 755` ⇄ `rwxr-xr-x`, dígitos y descripciones. |
| 🛠️ Construye el permiso | Marca las llaves r, w, x de usuario, grupo y otros. |
| ✅ Verdadero o falso | 26 afirmaciones con explicación. |
| 🧠 Quiz de teoría | 28 preguntas por bloques. |
| 🎯 ¿Te atreves? | Los 3 retos finales del PDF y 4 extra. |
| 🧪 Laboratorio | Bombillas, mezclador de color y permisos, sin puntos. |
| 📖 Chuleta | Resumen de teoría. |

Los ejercicios del entrenador, color y permisos **se generan al azar**, así que nunca se acaban.
Incluye puntos, racha 🔥, niveles (de *Bit* a *Root*) y precisión.

## 📁 Estructura

```
├── app.py            # Interfaz y lógica del juego
├── preguntas.py      # Contenido y generadores de ejercicios
├── requirements.txt  # Dependencias
└── README.md
```

## ▶️ Ejecutar en local

```bash
git clone https://github.com/TU_USUARIO/bit-quest.git
cd bit-quest
python -m venv .venv
source .venv/bin/activate      # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Publicarlo gratis (Streamlit Community Cloud)

1. Sube este proyecto a un repositorio **nuevo** de GitHub.
2. Entra en <https://share.streamlit.io> con tu cuenta de GitHub.
3. Pulsa **Create app**, elige el repositorio, rama `main` y archivo principal `app.py`.
4. Pulsa **Deploy** y comparte el enlace.

## ➕ Añadir contenido

Edita `preguntas.py`:

- **Verdadero/falso**: añade una tupla `("afirmación", True/False, "explicación")`.
- **Quiz**: copia una llamada a `_q(...)`.
- **Permisos para «Construye el permiso»**: añade una tupla `("descripción", "755")` a `CASOS_CHMOD`.
- **Colores con nombre**: añádelos a `NOMBRES_COLOR`.

## 👥 Autores

Manuel Ramos Perca · Joel Flores Lopez
