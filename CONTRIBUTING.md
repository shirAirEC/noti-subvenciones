# Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Notificaciones de Subvenciones BDNS!

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug:

1. Verifica que no esté ya reportado en Issues
2. Crea un nuevo Issue con:
   - Título descriptivo
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs relevantes
   - Versión/entorno

### Proponer Mejoras

Para nuevas funcionalidades:

1. Abre un Issue describiendo la propuesta
2. Espera feedback antes de implementar
3. Considera compatibilidad y mantenibilidad

### Pull Requests

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Realiza cambios siguiendo las guías de estilo
4. Escribe tests si es aplicable
5. Actualiza documentación
6. Commit con mensajes descriptivos
7. Push a tu fork
8. Abre un Pull Request

## Guías de Estilo

### Python

- Seguir PEP 8
- Usar type hints
- Docstrings para funciones públicas
- Nombres descriptivos en español para el dominio

```python
def obtener_subvenciones(
    finalidad: int,
    fecha_desde: date
) -> List[Subvencion]:
    """
    Obtener subvenciones de BDNS.
    
    Args:
        finalidad: ID de finalidad
        fecha_desde: Fecha de inicio
        
    Returns:
        Lista de subvenciones
    """
    pass
```

### JavaScript

- Usar ES6+
- Nombres descriptivos
- Comentarios para lógica compleja
- Manejo de errores consistente

### Commits

Formato: `tipo: descripción corta`

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato, espacios, etc.
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Mantenimiento

Ejemplos:
- `feat: añadir filtro por presupuesto`
- `fix: corregir error en envío de emails`
- `docs: actualizar guía de instalación`

## Estructura del Proyecto

```
.
├── backend/
│   ├── api/          # Endpoints REST
│   ├── models/       # Modelos SQLAlchemy
│   ├── services/     # Lógica de negocio
│   ├── tasks/        # Tareas programadas
│   └── scripts/      # Scripts de utilidad
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── docs/             # Documentación adicional
```

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=backend tests/

# Tests específicos
pytest tests/test_bdns_service.py
```

### Escribir Tests

```python
def test_obtener_subvenciones():
    """Test de obtención de subvenciones"""
    bdns = BDNSService()
    result = bdns.get_convocatorias(finalidad=11)
    assert result is not None
    assert len(result) > 0
```

## Áreas de Contribución

### Prioritarias

- [ ] Tests automatizados
- [ ] Mejora de filtros de búsqueda
- [ ] Optimización de rendimiento
- [ ] Internacionalización (i18n)
- [ ] Documentación de API

### Bienvenidas

- Correcciones de bugs
- Mejoras de UX/UI
- Optimizaciones de código
- Documentación
- Ejemplos de uso

### Ideas Futuras

- App móvil nativa
- Panel de administración
- Estadísticas y analytics
- Integración con Telegram
- Notificaciones push web

## Código de Conducta

- Ser respetuoso y constructivo
- Aceptar críticas constructivas
- Enfocarse en lo mejor para el proyecto
- Ayudar a otros contribuidores

## Preguntas

Si tienes preguntas sobre cómo contribuir, abre un Issue con la etiqueta `pregunta` o contacta a los mantenedores.

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la misma licencia del proyecto (MIT).

¡Gracias por contribuir! 🎉
