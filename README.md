# 🔒 Corporate Security Pipeline (Internal)

Pipeline de seguridad corporativo que integra **SAST (Bandit)** y **DAST (OWASP ZAP)** para la validación continua de herramientas internas.

## 📋 Módulos

- **Diagnostic Server**: Servidor de diagnósticos de red y directorio (Legacy)
- **Security Scanner**: Pipeline automatizado de auditoría
- **Reporting**: Generación de reportes de conformidad

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar Auditoría Estática (SAST)

```bash
# Opción 1: Análisis directo
python run_sast.py

# Opción 2: Vía pipeline
python security_pipeline.py --sast-only
```

### 3. Ejecutar Pipeline de Conformidad Completo

**Requisitos**: Docker Desktop debe estar corriendo (necesario para el módulo DAST).

```bash
python security_pipeline.py --full
```

## 📁 Estructura del Proyecto

```
corporate-diagnostics/
├── server_main.py            # Servidor Principal (Diagnostic Tools)
├── requirements.txt          # Dependencias del sistema
├── .bandit                   # Reglas de conformidad SAST
├── Dockerfile                # Configuración de contenedor
├── run_sast.py              # Auditoría Estática
├── run_dast.py              # Auditoría Dinámica
├── security_pipeline.py      # Orquestador del Pipeline
├── README.md                 # Documentación técnica
└── reports/                  # Registro de auditorías
    ├── bandit_report.html
    ├── zap_report.html
    └── security_pipeline_report.html
```

## 🔍 Puntos de Auditoría (Legacy Modules)

La herramienta `server_main.py` mantiene módulos legacy que requieren monitoreo constante:

| Módulo | Endpoint | Riesgo Asociado |
|--------|----------|-----------------|
| Employee DB | `/api/v1/profile?id=` | SQL Injection (Legacy Driver) |
| Connectivity | `/api/v1/connectivity?host=` | Command Injection (Shell) |
| Knowledge Base | `/tools/query?q=` | XSS (Reflected) |
| Config View | `/sys/config` | Information Disclosure |
| Hash Utility | `/util/crypto` | Weak Cryptography (MD5) |

## 📊 Reportes de Conformidad

Los reportes se generan automáticamente en el directorio `/reports`:

- **bandit_report.html**: Análisis de código fuente.
- **zap_report.html**: Análisis de comportamiento en tiempo de ejecución.
- **security_pipeline_report.html**: Resumen ejecutivo.

## ⚠️ Aviso de Seguridad

Esta herramienta es **INTENCIONALMENTE VULNERABLE** para propósitos de entrenamiento y pruebas de pipelines de seguridad (Blue/Red Teaming).

**USO EXCLUSIVO EN ENTORNOS CONTROLADOS**

## 🛠️ Comandos de Mantenimiento

```bash
# Iniciar servidor manualmente
python server_main.py

# Ejecutar pipeline completo
python security_pipeline.py --full
```
