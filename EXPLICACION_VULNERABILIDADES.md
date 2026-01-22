
## 🛡️ Análisis Detallado de Vulnerabilidades

Aquí tienes la explicación técnica de cada vulnerabilidad encontrada en el reporte y cómo solucionarla.

---

### 1. Command Injection (Inyección de Comandos)
**ID:** `B602` (Bandit) | **Severidad:** 🔴 CRÍTICA

**¿Qué es?**
El atacante puede ejecutar comandos del sistema operativo (Windows/Linux) en tu servidor. Es la vulnerabilidad más peligrosa.

**Código Vulnerable:**
```python
# app.py:146
subprocess.check_output(command, shell=True)
#                                ^^^^^^^^^^ PELIGRO
```

**El Ataque:**
Si `command` viene de un input de usuario (ej. "ping"), el atacante escribe:
`localhost & shutdown /s` -> ¡Apaga tu servidor!

**Solución:**
Nunca usar `shell=True`. Usar listas de argumentos:
```python
subprocess.check_output(["ping", "-n", "1", host])
```

---

### 2. SQL Injection (Inyección SQL)
**ID:** `B608` (Bandit) | **Severidad:** 🟠 ALTA

**¿Qué es?**
El atacante manipula tus consultas a la base de datos para ver, borrar o modificar datos que no debería.

**Código Vulnerable:**
```python
# app.py:111
query = f"SELECT * FROM users WHERE id = {user_id}"
#       ^ Strings f-strings concatenados
```

**El Ataque:**
Input: `1 OR 1=1`
Consulta resultante: `SELECT * FROM users WHERE id = 1 OR 1=1`
Resultado: Devuelve **TODOS** los usuarios, no solo el 1.

**Solución:**
Usar consultas parametrizadas (deja que la librería maneje los datos):
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

### 3. Weak Hashing (Hashing Débil)
**ID:** `B324` (Bandit) | **Severidad:** 🔴 ALTA

**¿Qué es?**
Los algoritmos MD5 y SHA1 están rotos. Se pueden "crackear" en milisegundos usando tarjetas gráficas modernas.

**Código Vulnerable:**
```python
# app.py:191
hashlib.md5(password.encode())
```

**Solución:**
Usar algoritmos lentos diseñados para passwords, como **Argon2** o **bcrypt**.
```python
import bcrypt
bcrypt.hashpw(password, bcrypt.gensalt())
```

---

### 4. Flask Debug Mode
**ID:** `B201` (Bandit) | **Severidad:** 🔴 ALTA

**¿Qué es?**
El modo debug de Flask muestra una consola interactiva en el navegador cuando hay un error.

**Código Vulnerable:**
```python
# app.py:260
app.run(debug=True)
```

**El Ataque:**
Si un atacante provoca un error, puede acceder a esa consola y ejecutar código Python arbitrario en tu servidor desde el navegador.

**Solución:**
Nunca usar `debug=True` en producción. Usar variables de entorno.
```python
debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
app.run(debug=debug_mode)
```

---

### 5. Content Security Policy (CSP) Missing
**Herramienta:** OWASP ZAP | **Severidad:** 🟠 MEDIA

**¿Qué es?**
Falta un header HTTP que le dice al navegador qué scripts son seguros para ejecutar.

**El Riesgo:**
Si un atacante logra inyectar un script (XSS), el navegador lo ejecutará porque no hay reglas que lo prohíban.

**Solución:**
Agregar el header en la respuesta:
`Content-Security-Policy: default-src 'self'`

---

### 6. Missing Anti-clickjacking Header
**Herramienta:** OWASP ZAP | **Severidad:** 🟠 MEDIA

**¿Qué es?**
Falta el header `X-Frame-Options` o CSP `frame-ancestors`.

**El Ataque:**
Un atacante puede poner tu sitio web dentro de un `<iframe>` invisible en su sitio malicioso. Cuando el usuario cree que está haciendo clic en un premio, en realidad está haciendo clic en tu sitio ("Like", "Transferir dinero", etc.).

**Solución:**
Agregar header:
`X-Frame-Options: DENY` o `SAMEORIGIN`
