# Guía Completa: Control de Almacén en Termux (Tablet Android)

Guía paso a paso desde la instalación de Termux hasta la compilación y ejecución de la aplicación en una tablet Android.

---

## Índice

1. [Instalar Termux](#1-instalar-termux)
2. [Configurar Termux](#2-configurar-termux)
3. [Clonar el Repositorio](#3-clonar-el-repositorio)
4. [Instalar Dependencias](#4-instalar-dependencias)
5. [Ejecutar la App (sin compilar)](#5-ejecutar-la-app-sin-compilar)
6. [Compilar el Ejecutable](#6-compilar-el-ejecutable)
7. [Ejecutar el Ejecutable](#7-ejecutar-el-ejecutable)
8. [Comandos y Atajos de Teclado](#8-comandos-y-atajos-de-teclado)
9. [Flujo de Uso](#9-flujo-de-uso)
10. [Solución de Problemas](#10-solución-de-problemas)
11. [Referencia Rápida](#11-referencia-rápida)

---

## 1. Instalar Termux

### Opción A: F-Droid (Recomendada)

1. Descargar **F-Droid** desde https://f-droid.org
2. Abrir F-Droid y buscar **"Termux"**
3. Tocar **Instalar**
4. Si pide permisos, aceptar "Fuentes desconocidas"

### Opción B: GitHub Releases

1. Ir a https://github.com/termux/termux-app/releases
2. Descargar el APK correspondiente a tu arquitectura:
   - `termux-app_v0.118.3+github-debug_arm64-v8a.apk` (la mayoría de tablets modernas)
   - `termux-app_v0.118.3+github-debug_armeabi-v7a.apk tablets viejas)
3. Abrir el APK y permitir instalación de fuentes desconocidas

> **IMPORTANTE**: NO usar Google Play. La versión de Google Play está desactualizada y tiene bugs conocidos.

---

## 2. Configurar Termux

### 2.1 Actualizar paquetes

```bash
pkg update && pkg upgrade -y
```

### 2.2 Instalar paquetes base

```bash
pkg install -y python git
```

### 2.3 Dar permisos de almacenamiento (opcional pero recomendado)

```bash
termux-setup-storage
```

Esto crea una carpeta `~/storage` con acceso a archivos de la tablet.

### 2.4 Configurar teclado para escáner Bluetooth

Si usás un escáner Bluetooth, asegurate de que esté pareado:

```bash
# Verificar dispositivos Bluetooth
bluetoothctl

# Dentro de bluetoothctl:
power on
scan on
# Esperar que aparezca el escáner
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
```

> El escáner Bluetooth actúa como teclado — cada escaneo escribe los caracteres + Enter automáticamente.

---

## 3. Clonar el Repositorio

### Opción A: Desde GitHub

```bash
cd ~
git clone https://github.com/usuario/control_almacen.git
cd control_almacen
```

### Opción B: Copiar archivos manualmente

Si no tenés Git o preferís copiar por USB/Bluetooth:

```bash
mkdir -p ~/control_almacen
cd ~/control_almacen
# Copiar todos los archivos .py, build.spec, pyproject.toml, etc.
```

### Opción C: Desde almacenamiento local (si copiaste vía USB)

```bash
cp -r /sdcard/control_almacen ~/control_almacen
cd ~/control_almacen
```

---

## 4. Instalar Dependencias

### 4.1 Instalar pip y las dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias de la app
pip install urwid openpyxl pyinstaller
```

### 4.2 Verificar instalación

```bash
python -c "import urwid; print('urwid:', urwid.__version__)"
python -c "import openpyxl; print('openpyxl:', openpyxl.__version__)"
python -c "import PyInstaller; print('PyInstaller:', PyInstaller.__version__)"
```

Debería mostrar las versiones de cada paquete sin errores.

---

## 5. Ejecutar la App (sin compilar)

### 5.1 Ejecución directa

```bash
python main.py tu_usuario
```

Reemplazá `tu_usuario` con tu nombre o identificador (ej: `Juan`, `OPERADOR01`).

### 5.2 Qué pasa al ejecutar

1. Se crea un archivo Excel: `deposito_YYYY-MM-DD_HHMM.xlsx`
2. Se abre la interfaz TUI con urwid
3. Podés empezar a escanear ubicaciones y artículos

### 5.3 Salir de la app

Presioná **F4** para salir en cualquier momento.

---

## 6. Compilar el Ejecutable

### 6.1 Compilar con el script automático

```bash
chmod +x build_termux.sh
./build_termux.sh
```

### 6.2 Compilar manualmente (paso a paso)

```bash
# Instalar dependencias
pip install urwid openpyxl pyinstaller

# Compilar
pyinstaller build.spec --clean
```

### 6.3 Ubicación del ejecutable

Después de compilar, el ejecutable queda en:

```
dist/ControlAlmacen
```

### 6.4 Verificar que funciona

```bash
./dist/ControlAlmacen tu_usuario
```

### 6.5 Tamaño del ejecutable

El binario pesa aproximadamente **30-50 MB** dependiendo de la arquitectura.

---

## 7. Ejecutar el Ejecutable

### 7.1 Dar permisos de ejecución

```bash
chmod +x dist/ControlAlmacen
```

### 7.2 Ejecutar

```bash
./dist/ControlAlmacen tu_usuario
```

### 7.3 Si el binario no funciona

Si el ejecutable compilado falla (problemas de compatibilidad), ejecutá directamente con Python:

```bash
python main.py tu_usuario
```

---

## 8. Comandos y Atajos de Teclado

### Atajos de la TUI

| Tecla | Acción | Disponible en |
|-------|--------|---------------|
| **Enter** | Confirmar entrada / procesar escaneo | Todos los estados |
| **Escape** | Limpiar campo de entrada | Todos los estados |
| **F1** | Ir a escanear ubicación (inicio) | Todos los estados |
| **F2** | Ver resumen de sesión | Todos los estados |
| **F4** | Salir de la aplicación | Todos los estados |

### Comandos de entrada por estado

| Estado | Entrada válida | Acción |
|--------|----------------|--------|
| **UBICACIÓN** | Código de 10 caracteres (ej: `DEP1A14702`) | Registra ubicación, pasa a ARTÍCULOS |
| **UBICACIÓN** | `0` | Muestra resumen de sesión |
| **ARTÍCULOS** | Código de 9 caracteres (ej: `ABC123456`) | Agrega artículo al lote actual |
| **ARTÍCULOS** | `0` | Muestra artículos cargados para confirmar |
| **CONFIRMACIÓN** | `0` | Guarda y vuelve a UBICACIÓN |
| **CONFIRMACIÓN** | `1` | Vuelve a escanear más artículos |
| **RESUMEN** | Cualquier tecla | Vuelve a UBICACIÓN |

### Comandos de Termux útiles

| Comando | Acción |
|---------|--------|
| `Ctrl+C` | Forzar salida (si la app no responde) |
| `Ctrl+Z` | Pausar app (puedes reanudar con `fg`) |
| `exit` | Cerrar Termux |
| `pwd` | Ver directorio actual |
| `ls` | Ver archivos |
| `cat archivo.xlsx` | No recomendado — usar la app |

---

## 9. Flujo de Uso

### Flujo completo típico

```
1. Abrir Termux
2. cd ~/control_almacen
3. python main.py OPERADOR01
4. ┌─────────────────────────────────────┐
   │ SISTEMA DE CONTROL DE ALMACÉN       │
   │ Usuario: OPERADOR01                 │
   ├─────────────────────────────────────┤
   │ Escanee la ubicación (10 caracteres)│
   │ INPUT: [DEP1A14702        ]         │
   ├─────────────────────────────────────┤
   │ Estado: SCAN LOCATION | Items: 0   │
   └─────────────────────────────────────┘
5. Escanear ubicación → Enter
6. Escanear artículos (uno por uno) → Enter
7. Ingresar 0 → Verificar lote
8. Ingresar 0 → Guardar
9. Repetir desde paso 4
10. F4 → Salir
```

### Formato de códigos

**Ubicación (10 caracteres):**
```
DEP1A14702
│   │  │  │
│   │  │  └─ Nivel (2 chars)
│   │  └─── Columna (2 chars)
│   └───── Pasillo (2 chars)
└────────── Depósito (4 chars)
```

**Artículo (9 caracteres):**
- Alfanumérico (letras y números)
- Longitud exacta: 9 caracteres

---

## 10. Solución de Problemas

### "No module named 'urwid'"

```bash
pip install urwid
```

### "No module named 'openpyxl'"

```bash
pip install openpyxl
```

### "Permission denied" al ejecutar el binario

```bash
chmod +x dist/ControlAlmacen
```

### "Python no se encuentra"

```bash
# Verificar que Python está instalado
python --version

# Si no está:
pkg install python
```

### "PyInstaller no se encuentra"

```bash
pip install pyinstaller
```

### El escáner Bluetooth no escribe

1. Verificar que esté pareado: `bluetoothctl`
2. Verificar que esté conectado
3. Probar escribiendo en Termux directamente — si el escáner escribe ahí, funciona
4. Algunos escáners necesitan modo HID — revisar manual del escáner

### El binario compilado no arranca

```bash
# Ejecutar con Python en vez del binario
python main.py tu_usuario

# O ver el error exacto
./dist/ControlAlmacen tu_usuario 2>&1
```

### "Error opening Excel"

- Verificar que no tengas el Excel abierto en otra app
- Verificar permisos de escritura en el directorio
- Intentar: `chmod 755 ~/control_almacen`

### Pantalla rota o caracteres raros

- Asegurar que Termux esté en pantalla completa
- Probar: `export LANG=en_US.UTF-8`
- Si usás escáner, verificar que no esté enviando caracteres extra

---

## 11. Referencia Rápida

### Comandos esenciales

```bash
# Instalación
pkg update && pkg upgrade -y
pkg install -y python git
pip install urwid openpyxl pyinstaller

# Ejecutar
python main.py USUARIO

# Compilar
pyinstaller build.spec --clean

# Ejecutable
./dist/ControlAlmacen USUARIO

# Salir
F4
```

### Estructura de archivos

```
control_almacen/
├── main.py              # Entry point
├── tui/
│   ├── __init__.py
│   ├── app.py           # Aplicación urwid (FSM)
│   ├── states.py        # Enum de estados
│   ├── widgets.py       # Widgets urwid
│   └── excel.py         # I/O Excel (openpyxl)
├── ubic.py              # Clase Ubic
├── rel_ubic.py          # Clase ProdUbic
├── validation.py        # Validadores
├── build.spec           # Config PyInstaller
├── build_termux.sh      # Script compilación Termux
├── Makefile             # Targets de build
└── pyproject.toml       # Dependencias
```

### Atajos de teclado (resumen)

```
Enter    → Confirmar
Escape   → Limpiar
F1       → Ubicación (inicio)
F2       → Resumen sesión
F4       → Salir
```

---

## Notas Finales

- **Backup**: Los archivos Excel se guardan en el mismo directorio donde ejecutás la app
- **Múltiples sesiones**: Cada ejecución crea un archivo nuevo con fecha/hora
- **Sin internet**: La app funciona 100% offline
- **Escáner**: El escáner Bluetooth escribe directamente en el campo de entrada
- **Recompilar**: Si modificás código, volvé a compilar con `pyinstaller build.spec --clean`
