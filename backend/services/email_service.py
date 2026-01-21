"""
Servicio de notificaciones por email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from jinja2 import Template
from loguru import logger
from backend.config import get_settings

settings = get_settings()


class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Enviar email
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_content: Contenido HTML
            text_content: Contenido de texto plano (opcional)
            
        Returns:
            True si se envió correctamente
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # Añadir versión texto plano
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            # Añadir versión HTML
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✓ Email enviado a {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {e}")
            return False
    
    def send_nueva_subvencion(
        self,
        to_email: str,
        nombre_usuario: str,
        subvencion: dict,
        calendar_url: str,
        unsubscribe_url: str
    ) -> bool:
        """
        Enviar notificación de nueva subvención
        
        Args:
            to_email: Email del destinatario
            nombre_usuario: Nombre del usuario
            subvencion: Datos de la subvención
            calendar_url: URL del calendario
            unsubscribe_url: URL para darse de baja
            
        Returns:
            True si se envió correctamente
        """
        subject = f"🔔 Nueva subvención: {subvencion['titulo']}"
        
        html_content = self._render_template_nueva_subvencion(
            nombre_usuario=nombre_usuario,
            subvencion=subvencion,
            calendar_url=calendar_url,
            unsubscribe_url=unsubscribe_url
        )
        
        text_content = self._render_text_nueva_subvencion(
            nombre_usuario=nombre_usuario,
            subvencion=subvencion,
            calendar_url=calendar_url,
            unsubscribe_url=unsubscribe_url
        )
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_confirmacion_suscripcion(
        self,
        to_email: str,
        nombre_usuario: str,
        token_confirmacion: str,
        calendar_url: str
    ) -> bool:
        """
        Enviar email de confirmación de suscripción
        
        Args:
            to_email: Email del destinatario
            nombre_usuario: Nombre del usuario
            token_confirmacion: Token para confirmar
            calendar_url: URL del calendario
            
        Returns:
            True si se envió correctamente
        """
        subject = "✅ Confirma tu suscripción a Subvenciones de Investigación"
        
        confirm_url = f"{settings.frontend_url}/confirmar?token={token_confirmacion}"
        
        html_content = self._render_template_confirmacion(
            nombre_usuario=nombre_usuario,
            confirm_url=confirm_url,
            calendar_url=calendar_url
        )
        
        return self.send_email(to_email, subject, html_content)
    
    def _render_template_nueva_subvencion(
        self,
        nombre_usuario: str,
        subvencion: dict,
        calendar_url: str,
        unsubscribe_url: str
    ) -> str:
        """Renderizar template HTML para nueva subvención"""
        template = Template('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nueva Subvención</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .subvencion { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .fecha { color: #e74c3c; font-weight: bold; font-size: 1.1em; margin: 15px 0; }
        .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
        .footer { text-align: center; margin-top: 30px; color: #777; font-size: 0.9em; }
        .info-row { margin: 10px 0; }
        .label { font-weight: bold; color: #555; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔔 Nueva Subvención Disponible</h1>
    </div>
    <div class="content">
        <p>Hola {{ nombre_usuario }},</p>
        <p>Hemos detectado una nueva subvención que coincide con tus intereses:</p>
        
        <div class="subvencion">
            <h2>{{ subvencion.titulo }}</h2>
            
            {% if subvencion.descripcion %}
            <p>{{ subvencion.descripcion }}</p>
            {% endif %}
            
            <div class="info-row">
                <span class="label">📋 Órgano convocante:</span> {{ subvencion.organo_convocante or 'No especificado' }}
            </div>
            
            {% if subvencion.region_nombre %}
            <div class="info-row">
                <span class="label">🌍 Región:</span> {{ subvencion.region_nombre }}
            </div>
            {% endif %}
            
            {% if subvencion.presupuesto_total %}
            <div class="info-row">
                <span class="label">💰 Presupuesto:</span> {{ "%.2f"|format(subvencion.presupuesto_total) }} €
            </div>
            {% endif %}
            
            <div class="fecha">
                ⏰ Fecha límite: {{ subvencion.fecha_fin_solicitud.strftime('%d/%m/%Y') if subvencion.fecha_fin_solicitud else 'Por determinar' }}
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <a href="{{ subvencion.url_bdns }}" class="button">📄 Ver Convocatoria en BDNS</a>
                <a href="{{ calendar_url }}" class="button">📅 Ver en Calendario</a>
            </div>
        </div>
        
        <p>Esta subvención se ha añadido automáticamente al <a href="{{ calendar_url }}">calendario compartido</a>. Recibirás recordatorios automáticos conforme se acerque la fecha límite.</p>
    </div>
    
    <div class="footer">
        <p>Este es un mensaje automático del Sistema de Notificaciones de Subvenciones.</p>
        <p><a href="{{ unsubscribe_url }}">Cancelar suscripción</a></p>
    </div>
</body>
</html>
        ''')
        
        return template.render(
            nombre_usuario=nombre_usuario,
            subvencion=subvencion,
            calendar_url=calendar_url,
            unsubscribe_url=unsubscribe_url
        )
    
    def _render_text_nueva_subvencion(
        self,
        nombre_usuario: str,
        subvencion: dict,
        calendar_url: str,
        unsubscribe_url: str
    ) -> str:
        """Renderizar versión texto plano"""
        fecha_fin = subvencion.get('fecha_fin_solicitud')
        fecha_str = fecha_fin.strftime('%d/%m/%Y') if fecha_fin else 'Por determinar'
        
        text = f"""
Hola {nombre_usuario},

Nueva subvención disponible:

TÍTULO: {subvencion['titulo']}

ÓRGANO CONVOCANTE: {subvencion.get('organo_convocante', 'No especificado')}

REGIÓN: {subvencion.get('region_nombre', 'No especificada')}

PRESUPUESTO: {subvencion.get('presupuesto_total', 'No especificado')} €

⏰ FECHA LÍMITE: {fecha_str}

Ver más información:
{subvencion['url_bdns']}

Ver calendario:
{calendar_url}

---
Para cancelar tu suscripción: {unsubscribe_url}
        """
        return text.strip()
    
    def _render_template_confirmacion(
        self,
        nombre_usuario: str,
        confirm_url: str,
        calendar_url: str
    ) -> str:
        """Renderizar template de confirmación"""
        template = Template('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; padding: 15px 40px; background: #27ae60; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-size: 1.1em; }
        .info { background: #e8f5e9; padding: 15px; border-left: 4px solid #27ae60; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ Confirma tu Suscripción</h1>
    </div>
    <div class="content">
        <p>Hola {{ nombre_usuario }},</p>
        <p>¡Gracias por suscribirte a nuestro sistema de notificaciones de subvenciones!</p>
        
        <p>Para activar tu suscripción, haz clic en el siguiente botón:</p>
        
        <div style="text-align: center;">
            <a href="{{ confirm_url }}" class="button">Confirmar Suscripción</a>
        </div>
        
        <div class="info">
            <h3>📅 Acceso al Calendario</h3>
            <p>Una vez confirmada tu suscripción, podrás acceder al calendario compartido de subvenciones:</p>
            <p><a href="{{ calendar_url }}">Ver Calendario de Subvenciones</a></p>
        </div>
        
        <h3>¿Qué recibirás?</h3>
        <ul>
            <li>✉️ Notificaciones por email de nuevas subvenciones que coincidan con tus filtros</li>
            <li>📅 Eventos automáticos en el calendario compartido</li>
            <li>🔔 Recordatorios de fechas límite</li>
        </ul>
        
        <p>Si no solicitaste esta suscripción, puedes ignorar este mensaje.</p>
    </div>
</body>
</html>
        ''')
        
        return template.render(
            nombre_usuario=nombre_usuario,
            confirm_url=confirm_url,
            calendar_url=calendar_url
        )
