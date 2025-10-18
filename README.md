
# Code Translator API

API REST para traducir código entre C++ y C# usando zzzcode.ai con Selenium.

## 🚀 Despliegue en Replit

### Paso 1: Crear el Repl
1. Ve a [Replit](https://replit.com)
2. Click en "Create Repl"
3. Selecciona "Import from GitHub" o "Python"
4. Sube los archivos del proyecto

### Paso 2: Configuración automática
El archivo `.replit` configurará automáticamente:
- Python 3.11
- Chromium y ChromeDriver
- Dependencias del sistema

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```


### Paso 4: Ejecutar
```python
python main.py
```

## 📡 Endpoints
### `POST /api/translate`
Traduce código entre lenguajes.
**Request:**
```JSON
{
  "code": "código fuente",
  "direction": "cpp_to_cs | cs_to_cpp",
  "mode": "game | study"
}
```

**Response:**
```JSON
{
  "success": true,
  "translated_code": "código traducido",
  "from_lang": "C++",
  "to_lang": "C#"
}
```
### `GET /api/health`
Verifica el estado del servidor.
### `GET /api/stats`
Obtiene estadísticas de uso.
## 🔧 Uso desde CodePen o similar
```jscript
const API_URL = 'https://tu-repl.usuario.repl.co';

async function translateCode(code, direction = 'cpp_to_cs') {
    const response = await fetch(`${API_URL}/api/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, direction, mode: 'game' })
    });
    
    const data = await response.json();
    return data.translated_code;
}
```

## 📝 Notas
- El servidor corre en el puerto 8080
- Replit proporciona HTTPS automáticamente
- El plan gratuito puede "dormirse" después de inactividad
- Primera ejecución puede tardar en cargar Chrome

## 🐛 Troubleshooting
Si Chrome no se encuentra:
1. Verifica que `replit.nix` esté correctamente configurado
2. Reinicia el Repl
3. Revisa los logs en la consola

## 📄 Licencia
MIT

## **2. Pasos para subir a Replit**

### **Opción A: Subir archivos manualmente**

1. **Ve a [Replit](https://replit.com)** y crea una cuenta si no la tienes
2. **Click en "Create Repl"**
3. **Selecciona "Python"** como template
4. **Nombra tu Repl**: `code-translator-api`
5. **Sube los archivos**:
   - Arrastra y suelta todos los archivos (menos `.venv` y `__pycache__`)
   - O usa el botón de upload en el explorador de archivos

6. **Archivos que debes subir**:
   ```
   ✅ main.py
   ✅ api_server.py
   ✅ zzzcode_translator.py
   ✅ start_server.py
   ✅ requirements.txt
   ✅ .replit
   ✅ replit.nix
   ✅ README.md
   ❌ .venv/ (NO subir)
   ❌ __pycache__/ (NO subir)
   ❌ .env (NO subir - contiene secrets)
   ```

### **Opción B: Desde GitHub (Recomendado)**

1. **Sube tu código a GitHub primero**:

En tu máquina local
```bash
git init 
git add . 
git commit -m "Initial commit" 
git branch -M main 
git remote add origin https://github.com/tu-usuario/code-translator-api.git 
git push -u origin main
```

2. **En Replit**:
   - Click "Create Repl"
   - Selecciona "Import from GitHub"
   - Pega la URL de tu repositorio
   - Click "Import from GitHub"

## **3. Configurar y ejecutar en Replit**

1. **Espera a que Replit instale las dependencias** (automático con `replit.nix`)

2. **Si no se instalan automáticamente, ejecuta en la Shell**:
```bash
pip install -r requirements.txt
```

4. **Obtener tu URL pública**:
   - Replit te mostrará la URL en la pestaña "Webview"
   - Será algo como: `https://code-translator-api.tu-usuario.repl.co`

## **4. Actualizar tu código de CodePen**

Una vez que tengas la URL de Replit:

```javascript
// En CodePen
const API_URL = 'https://code-translator-api.tu-usuario.repl.co';

async function translateCode(code, direction = 'cpp_to_cs', mode = 'game') {
    try {
        const response = await fetch(`${API_URL}/api/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, direction, mode })
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.translated_code;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error traduciendo código:', error);
        throw error;
    }
}
```

## **5. Mantener el Repl activo (opcional)**

Replit gratuito "duerme" después de inactividad. Para mantenerlo activo:

### **Opción 1: UptimeRobot (Gratis)**
1. Ve a [UptimeRobot](https://uptimerobot.com)
2. Crea un monitor HTTP(S)
3. URL: `https://tu-repl.repl.co/api/health`
4. Intervalo: 5 minutos

### **Opción 2: Actualizar a Replit Hacker Plan**
- $7/mes
- Siempre activo
- Más recursos

