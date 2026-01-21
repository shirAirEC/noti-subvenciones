# Guía de Despliegue

Guía para desplegar el Sistema de Notificaciones de Subvenciones en producción.

## Opciones de Despliegue

1. Servidor VPS (DigitalOcean, Linode, etc.)
2. Cloud Providers (AWS, GCP, Azure)
3. Plataformas PaaS (Heroku, Railway, Render)

## Despliegue en VPS con Docker

### Requisitos

- Ubuntu 22.04 LTS (recomendado)
- Mínimo 2GB RAM
- 20GB disco
- Dominio (opcional pero recomendado)

### 1. Preparar Servidor

```bash
# Conectar por SSH
ssh usuario@tu-servidor

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar herramientas
sudo apt install -y git make
```

### 2. Clonar Repositorio

```bash
cd /opt
sudo git clone <tu-repositorio> subvenciones
sudo chown -R $USER:$USER subvenciones
cd subvenciones
```

### 3. Configurar Producción

```bash
cp .env.docker.example .env
nano .env
```

Configurar variables para producción:

```env
# Base de datos - usar password fuerte
POSTGRES_PASSWORD=<generar-password-seguro>

# Google Calendar
CALENDAR_ID=<tu-calendar-id>

# Email
EMAIL_FROM=noreply@tu-dominio.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<email>
SMTP_PASSWORD=<app-password>

# Frontend - usar tu dominio
FRONTEND_URL=https://tu-dominio.com

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=8
SCHEDULER_MINUTE=0

# Logging
LOG_LEVEL=INFO
```

### 4. Configurar Credenciales Google

```bash
mkdir -p credentials
nano credentials/service-account.json
# Pegar el contenido del archivo JSON
chmod 600 credentials/service-account.json
```

### 5. Configurar Firewall

```bash
# Permitir SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 6. Configurar Nginx y SSL (Opcional)

Si quieres usar un dominio con HTTPS:

```bash
# Instalar Nginx y Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Configurar renovación automática
sudo systemctl enable certbot.timer
```

Crear configuración de Nginx:

```nginx
# /etc/nginx/sites-available/subvenciones
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/subvenciones /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Iniciar Aplicación

```bash
# Construir imágenes
make build

# Iniciar servicios
make start

# Verificar
docker-compose ps
docker-compose logs -f
```

### 8. Inicializar Base de Datos

```bash
docker-compose exec backend python backend/scripts/populate_catalogs.py
```

### 9. Configurar Systemd (Arranque Automático)

```bash
sudo nano /etc/systemd/system/subvenciones.service
```

```ini
[Unit]
Description=Sistema de Notificaciones de Subvenciones
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/subvenciones
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable subvenciones
sudo systemctl start subvenciones
```

## Monitoreo y Mantenimiento

### Ver Logs

```bash
# Logs en tiempo real
docker-compose logs -f

# Logs específicos
docker-compose logs backend
docker-compose logs postgres
docker-compose logs frontend
```

### Backups

#### Base de datos

```bash
# Crear directorio de backups
mkdir -p /opt/backups

# Script de backup
cat > /opt/backups/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
docker-compose exec -T postgres pg_dump -U subvenciones_user subvenciones | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/backups/backup.sh

# Cron para backups diarios
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backups/backup.sh") | crontab -
```

#### Restaurar backup

```bash
gunzip < /opt/backups/db_FECHA.sql.gz | docker-compose exec -T postgres psql -U subvenciones_user subvenciones
```

### Actualizar Aplicación

```bash
cd /opt/subvenciones
git pull
make build
make restart
```

### Monitoreo de Recursos

```bash
# Uso de recursos
docker stats

# Espacio en disco
df -h

# Limpiar imágenes antiguas
docker system prune -a
```

## Seguridad

### 1. Actualizar regularmente

```bash
# Sistema
sudo apt update && sudo apt upgrade -y

# Docker
sudo apt install docker-ce docker-ce-cli containerd.io

# Aplicación
cd /opt/subvenciones && git pull && make build && make restart
```

### 2. Restringir acceso SSH

```bash
# Usar solo autenticación por clave
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart sshd
```

### 3. Configurar fail2ban

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Limitar acceso a PostgreSQL

PostgreSQL debe estar solo accesible desde localhost (configurado por defecto en docker-compose).

## Troubleshooting Producción

### Error 502 Bad Gateway

- Verificar que backend está corriendo: `docker-compose ps`
- Verificar logs: `docker-compose logs backend`
- Reiniciar: `docker-compose restart backend`

### Alto uso de memoria

- Aumentar recursos del servidor
- Ajustar configuración de PostgreSQL
- Revisar logs para memory leaks

### Error en scheduler

- Verificar logs: `docker-compose logs backend | grep scheduler`
- Ejecutar sincronización manual: `make sync-now`
- Verificar conexión a BDNS API

## Escalabilidad

### Para mayor tráfico:

1. **Separar servicios**: PostgreSQL en servidor dedicado
2. **Load balancer**: Nginx para múltiples instancias de backend
3. **Redis**: Para caché y cola de tareas
4. **CDN**: Para archivos estáticos del frontend

### Configuración multi-servidor

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      DATABASE_URL: postgresql://user:pass@db-servidor:5432/subvenciones
```

## Contacto y Soporte

Para problemas en producción, consulta los logs y la documentación. Abre un issue en el repositorio si necesitas ayuda.
