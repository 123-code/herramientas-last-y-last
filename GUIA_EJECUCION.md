# 🚀 Guía de Ejecución: Pipeline de Seguridad

Aquí tienes los pasos exactos para ejecutar el pipeline de seguridad en tu máquina.

## ✅ Requisitos Previos

1. **Docker Desktop**: Debe estar abierto y corriendo (busca el ícono de la ballena en tu barra de tareas).
2. **Terminal**: PowerShell o CMD.

---

## ⚡ Opción 1: Ejecución Automática (Recomendada)

Hemos creado un script que hace todo por ti.

1. Abre la carpeta del proyecto en el Explorador de Archivos.
   Ruta: `C:\Users\mateo\.gemini\antigravity\scratch\security-pipeline-demo`
2. Haz doble clic en el archivo **`ejecutar_pipeline.bat`**.

**¿Qué pasará?**
- Se abrirá una ventana negra (terminal).
- Verás el progreso del análisis SAST (Bandit).
- Verás el progreso del análisis DAST (ZAP) descargando la imagen de Docker.
- Al finalizar, **se abrirán automáticamente los reportes HTML** en tu navegador.

---

## 🛠️ Opción 2: Ejecución Manual (Paso a Paso)

Si prefieres usar la terminal y ver qué pasa comando por comando:

### 1. Preparar el entorno
Abre tu terminal y ve a la carpeta del proyecto:
```powershell
cd C:\Users\mateo\.gemini\antigravity\scratch\security-pipeline-demo
```

### 2. Ejecutar Pipeline Completo
Usamos el script de Python que orquesta todo:
```powershell
python security_pipeline.py --full
```

### 3. Ejecutar Por Partes (Opcional)

**Solo Análisis SAST (Código):**
```powershell
python run_sast.py
# O revisa ejecutar_sast.bat
```

**Solo Análisis DAST (Web en vivo):**
Primero asegúrate que tu app esté corriendo en una terminal (`python app.py`), luego en otra terminal:
```powershell
python run_dast.py
# O revisa ejecutar_dast.bat
```

---

## 📊 Dónde ver los resultados

Todos los reportes se guardan en la carpeta `reports/`:

| Archivo | Descripción |
|---------|-------------|
| **`security_pipeline_report.html`** | 🏅 **Reporte Principal**: Resumen de todo el pipeline. |
| `bandit_report.html` | 📄 Detalles técnicos del código (SAST). |
| `zap_report.html` | 🌐 Detalles técnicos de la web (DAST). |

---

## 🆘 Solución de Problemas Comunes

**Error: "Docker no está corriendo" o "Failed to connect to docker port"**
- **Solución**: Abre la aplicación "Docker Desktop" en Windows y espera a que el ícono de la ballena deje de animarse y se ponga verde/blanco.

**Error: "Python no se reconoce"**
- **Solución**: Asegúrate de tener Python instalado y agregado al PATH de Windows.
