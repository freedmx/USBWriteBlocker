# Validación Forense del Bloqueador de Escritura USB

## 1. Resumen Ejecutivo

Este documento tiene como propósito certificar y describir la validez técnica y forense del software “Bloqueador de Escritura USB”. Esta herramienta fue desarrollada para ser usada en entornos forenses con el objetivo de prevenir la escritura en dispositivos de almacenamiento USB mediante la modificación controlada del Registro de Windows. Su uso permite garantizar la preservación de la evidencia digital conforme a las mejores prácticas establecidas por organismos como SWGDE e ISO/IEC.

---

## 2. Objetivo

Prevenir la alteración de datos en unidades USB conectadas al sistema, bloqueando toda escritura hacia el dispositivo desde el sistema operativo, asegurando así la preservación de evidencias digitales contenidas en dispositivos extraíbles.

---

## 3. Justificación Técnica y Forense

Durante el análisis forense, es esencial preservar la integridad de la evidencia. Esta herramienta actúa como bloqueador de escritura software, evitando cualquier alteración involuntaria de la evidencia contenida en un dispositivo USB.

Referencias relevantes:

- **SWGDE – Best Practices for Computer Forensics**  
- **ISO/IEC 27037 – Guidelines for Identification, Collection, Acquisition and Preservation of Digital Evidence**  
- **NIST SP 800-86 – Guide to Integrating Forensic Techniques into Incident Response**

---

## 4. Metodología Aplicada

El software modifica la siguiente clave del registro de Windows:
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\StorageDevicePolicies
Valor: WriteProtect (DWORD)


### Acciones:

- Valor `1` → Activa protección contra escritura  
- Valor `0` → Desactiva protección contra escritura  
- Valor ausente → Se considera que no hay protección

Este cambio se aplica globalmente a todas las unidades de almacenamiento USB conectadas al sistema.

---

## 5. Procedimiento Técnico

- Verifica si la aplicación se ejecuta con privilegios de administrador.
- Crea la clave del registro si no existe.
- Establece o elimina el valor `WriteProtect` según la acción del usuario.
- Muestra en tiempo real un registro en pantalla con marca de tiempo.
- La interfaz gráfica permite al usuario:
  - Activar protección
  - Desactivar protección
  - Ver el estado actual
  - Consultar logs del sistema

---

## 6. Validación y Verificabilidad

La herramienta ha sido validada mediante los siguientes métodos:

- **Auditoría del registro:** Confirmación visual con `regedit.exe` posterior a la operación.
- **Pruebas funcionales:** Inserción de unidad USB con intento de copia de archivo (fallida si la protección está activada).
- **Código abierto:** El código fuente puede ser revisado por cualquier parte interesada.
- **Bitácora en tiempo real:** Incluye timestamps y mensajes detallados en pantalla.
- **Verificación por hash:** El archivo fuente principal puede ser verificado con un hash SHA256 para garantizar su integridad.

---

## 7. Limitaciones

- Solo funciona en sistemas **Microsoft Windows**.
- Requiere derechos de **administrador** para aplicar los cambios.
- No bloquea la **lectura** de dispositivos USB, solo la escritura.
- No sustituye a bloqueadores físicos cuando estos son requeridos formalmente por normativa judicial.

---

## 8. Entorno Recomendado

- Sistemas operativos compatibles: Windows 10 / 11 (x64)
- Uso en laboratorios forenses o auditorías informáticas
- Debe ejecutarse **antes de insertar** cualquier unidad USB
- No debe alterarse el sistema mientras esté en ejecución

---

## 9. Licenciamiento

Este software se distribuye bajo los términos de la **Licencia Pública General GNU v3 (GPL v3)**. Esto garantiza:

- Libertad para usarlo con fines personales o profesionales
- Libertad para modificar el código fuente
- Obligación de mantener la autoría original y las condiciones de licencia si se redistribuye

---

## 10. Referencias Normativas

- [SWGDE Best Practices for Computer Forensics (2023)](https://www.swgde.org/documents/published)
- [ISO/IEC 27037:2012](https://www.iso.org/standard/44381.html)
- [NIST SP 800-86](https://csrc.nist.gov/publications/detail/sp/800-86/final)
- [Documentación Microsoft sobre StorageDevicePolicies](https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-storagedevicepolicies)

---

## 11. Declaración Final

Esta herramienta ha sido diseñada con el propósito de **preservar la integridad de evidencias digitales** en entornos forenses y de ciberseguridad. El desarrollador no se hace responsable del uso inadecuado del software. Se recomienda al usuario validar siempre el entorno de ejecución y verificar los efectos del bloqueo antes de utilizarlo en procesos judiciales.


