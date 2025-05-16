# Script para configurar la integración con Notion

# Verificar si Node.js está instalado
try {
    $nodeVersion = & "C:\Program Files\nodejs\node.exe" --version
    Write-Host "Node.js está instalado: $nodeVersion"
} catch {
    Write-Host "Error: Node.js no está instalado en la ruta esperada."
    Write-Host "Por favor, instala Node.js desde https://nodejs.org/"
    exit 1
}

# Instalar el paquete de Notion MCP Server
Write-Host "Instalando el paquete de Notion MCP Server..."
try {
    & "C:\Program Files\nodejs\npm.cmd" install -g @notionhq/notion-mcp-server
    Write-Host "Paquete instalado correctamente."
} catch {
    Write-Host "Error al instalar el paquete: $_"
    exit 1
}

# Instrucciones para obtener un token de Notion
Write-Host ""
Write-Host "======================= INSTRUCCIONES ======================="
Write-Host "Para completar la configuración, necesitas un token de Notion:"
Write-Host ""
Write-Host "1. Ve a https://www.notion.so/my-integrations"
Write-Host "2. Haz clic en '+ New integration'"
Write-Host "3. Dale un nombre como 'Catastro de Propiedades'"
Write-Host "4. Selecciona el workspace donde lo usarás"
Write-Host "5. Haz clic en 'Submit'"
Write-Host "6. Copia el 'Internal Integration Token'"
Write-Host ""
Write-Host "Luego, edita el archivo de configuración en:"
Write-Host "c:\Users\YBUSTAMANTEC\.codeium\windsurf\mcp_config.json"
Write-Host ""
Write-Host "Reemplaza 'secret_REEMPLAZA_ESTO_CON_TU_TOKEN_REAL' con tu token real"
Write-Host "============================================================="

# Preguntar si quiere abrir el archivo de configuración
$respuesta = Read-Host "¿Quieres abrir el archivo de configuración ahora? (s/n)"
if ($respuesta -eq "s") {
    notepad "c:\Users\YBUSTAMANTEC\.codeium\windsurf\mcp_config.json"
}

Write-Host "Configuración completada. Reinicia tu aplicación para aplicar los cambios."
