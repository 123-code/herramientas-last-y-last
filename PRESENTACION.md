# 🔒 Corporate Security Review Pipeline
## Protocolo de Auditoría Automatizada

---

## 📋 Agenda

1. [Visión General](#visión-general)
2. [Arquitectura de Seguridad](#arquitectura-de-seguridad)
3. [Fase 1: Auditoría Estática (SAST)](#fase-1-auditoría-estática-sast)
4. [Fase 2: Ejecución del Entorno](#fase-2-ejecución-del-entorno)
5. [Fase 3: Auditoría Dinámica (DAST)](#fase-3-auditoría-dinámica-dast)
6. [Reporte de Conformidad](#reporte-de-conformidad)

---

## Visión General

Este sistema implementa un pipeline de "Compliance-as-Code" utilizando herramientas estándar de la industria:

| Componente | Herramienta | Función |
|------------|-------------|---------|
| **SAST** | Bandit | Auditoría de código fuente y configuración |
| **DAST** | OWASP ZAP | Auditoría de superficie de ataque externa |

### Flujo de Trabajo

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Server Code │─────▶│    SAST      │─────▶│   Reporte    │
│    Python    │      │   (Bandit)   │      │   Técnico    │
└──────────────┘      └──────────────┘      └──────────────┘
       │
       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Live App    │─────▶│    DAST      │─────▶│   Reporte    │
│  (Docker)    │      │  (OWASP ZAP) │      │   Ejecutivo  │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## Fase 1: Auditoría Estática (SAST)

### Ejecución del Escáner

```powershell
python -m bandit -r server_main.py -f html -o reports/bandit_report.html
```

### Hallazgos Típicos (Legacy Code)

El análisis estático detecta patrones no conformes en el código del servidor:

*   **High Severity**: Uso de `subprocess` con `shell=True` (Módulo Connectivity).
*   **High Severity**: Uso de algoritmos de hash `MD5`/`SHA1` (Módulo Crypto).
*   **Medium Severity**: Construcción manual de consultas SQL (Módulo Employee DB).

---

## Fase 2: Ejecución del Entorno

### Iniciar Servidor de Diagnóstico

```powershell
python server_main.py
```

**Consola:**
```
 * Corporate Diagnostic Server v3.0.1
 * Running on http://0.0.0.0:5000
```

### Interfaz Corporativa

Accesible vía: `http://localhost:5000`

La nueva interfaz "CorpNet Diagnostics" presenta las herramientas internas disponibles para el personal autorizado.

---

## Fase 3: Auditoría Dinámica (DAST)

### Ejecución de OWASP ZAP

El escáner dinámico interactúa con la aplicación viva para detectar vulnerabilidades en tiempo de ejecución.

```powershell
docker run --rm -v "%cd%\reports:/zap/wrk:rw" --add-host=host.docker.internal:host-gateway ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:5000 -r zap_report.html -I
```

### Superficie de Ataque Identificada

| Endpoint | Vector de Ataque | Descripción |
|----------|------------------|-------------|
| `/api/v1/profile` | SQL Injection | Extracción de datos de usuarios |
| `/api/v1/connectivity` | OS Command Injection | Ejecución remota de comandos |
| `/tools/query` | XSS (Reflected) | Inyección de scripts en navegador |
| `/sys/config` | Info Disclosure | Exposición de variables de entorno |

---

## Reporte de Conformidad

### Resultados Consolidados

El pipeline genera un reporte unificado en `reports/security_pipeline_report.html` que detalla el estado de seguridad de la aplicación.

*   **Estado General**: ❌ NO CONFORME (Múltiples hallazgos críticos)
*   **Acción Recomendada**: Remediación inmediata de módulos legacy.

---

## Conclusión Técnica

La implementación de este pipeline permite:
1.  **Detección Temprana**: Identificar riesgos en el código antes del despliegue.
2.  **Validación Continua**: Asegurar que nuevos cambios no introduzcan regresiones.
3.  **Visibilidad**: Proveer métricas claras sobre la postura de seguridad.

*Corporate Security Engineering*
