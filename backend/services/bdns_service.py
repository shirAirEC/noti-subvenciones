"""
Servicio de integración con la API de BDNS
"""
import httpx
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from loguru import logger
from backend.config import get_settings

settings = get_settings()


class BDNSService:
    """Cliente para la API de BDNS"""
    
    def __init__(self):
        self.base_url = settings.bdns_api_url
        self.timeout = 30.0
        
    async def get_convocatorias(
        self,
        finalidad: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        regiones: Optional[List[int]] = None,
        descripcion: Optional[str] = None,
        page: int = 0,
        page_size: int = 50,
        tipo_administracion: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtener convocatorias de BDNS con filtros
        
        Args:
            finalidad: ID de finalidad (ej: investigación)
            fecha_desde: Fecha de inicio de búsqueda
            fecha_hasta: Fecha de fin de búsqueda
            regiones: Lista de IDs de regiones
            descripcion: Búsqueda por texto en título
            page: Número de página
            page_size: Tamaño de página
            tipo_administracion: C=Estado, A=CCAA, L=Local, O=Otros
            
        Returns:
            Diccionario con resultados y metadata
        """
        endpoint = f"{self.base_url}/convocatorias/busqueda"
        
        params = {
            "page": page,
            "pageSize": page_size,
            "vpd": "GE",  # Portal general
            "order": "fechaRecepcion",
            "direccion": "desc"
        }
        
        # Añadir filtros opcionales
        if finalidad:
            params["finalidad"] = finalidad
            
        if fecha_desde:
            params["fechaDesde"] = fecha_desde.strftime("%d/%m/%Y")
            
        if fecha_hasta:
            params["fechaHasta"] = fecha_hasta.strftime("%d/%m/%Y")
            
        if regiones:
            params["regiones"] = regiones
            
        if descripcion:
            params["descripcion"] = descripcion
            params["descripcionTipoBusqueda"] = 1  # Todas las palabras
            
        if tipo_administracion:
            params["tipoAdministracion"] = tipo_administracion
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                
                logger.info(
                    f"BDNS API: Obtenidas {len(data.get('convocatorias', []))} convocatorias "
                    f"(página {page}, total: {data.get('totalElementos', 0)})"
                )
                
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Error al consultar BDNS API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al consultar BDNS: {e}")
            raise
    
    async def get_convocatoria_detalle(self, id_bdns: str) -> Dict[str, Any]:
        """
        Obtener detalle de una convocatoria específica
        
        Args:
            id_bdns: ID de la convocatoria en BDNS
            
        Returns:
            Diccionario con datos detallados
        """
        endpoint = f"{self.base_url}/convocatorias"
        params = {
            "vpd": "GE",
            "numeroConvocatoria": id_bdns
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error al obtener detalle de convocatoria {id_bdns}: {e}")
            raise
    
    async def get_finalidades(self) -> List[Dict[str, Any]]:
        """
        Obtener catálogo de finalidades de BDNS
        
        Returns:
            Lista de finalidades
        """
        endpoint = f"{self.base_url}/finalidades"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Obtenidas {len(data)} finalidades de BDNS")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Error al obtener finalidades: {e}")
            raise
    
    async def get_regiones(self) -> List[Dict[str, Any]]:
        """
        Obtener catálogo de regiones de BDNS
        
        Returns:
            Lista de regiones
        """
        endpoint = f"{self.base_url}/regiones"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Obtenidas {len(data)} regiones de BDNS")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Error al obtener regiones: {e}")
            raise
    
    async def get_beneficiarios(self) -> List[Dict[str, Any]]:
        """
        Obtener catálogo de tipos de beneficiarios
        
        Returns:
            Lista de tipos de beneficiarios
        """
        endpoint = f"{self.base_url}/beneficiarios"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Obtenidos {len(data)} tipos de beneficiarios")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Error al obtener tipos de beneficiarios: {e}")
            raise
    
    def parse_convocatoria(self, conv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsear datos de convocatoria de BDNS a formato interno
        
        Args:
            conv_data: Datos crudos de la API
            
        Returns:
            Diccionario con datos parseados
        """
        # Parsear fechas
        def parse_date(date_str: Optional[str]) -> Optional[datetime]:
            if not date_str:
                return None
            try:
                # Formato: dd/mm/yyyy o timestamp
                if '/' in date_str:
                    return datetime.strptime(date_str, "%d/%m/%Y")
                else:
                    return datetime.fromtimestamp(int(date_str) / 1000)
            except Exception:
                return None
        
        parsed = {
            "id_bdns": str(conv_data.get("numeroConvocatoria", "")),
            "titulo": conv_data.get("descripcion", ""),
            "descripcion": conv_data.get("objeto", ""),
            "fecha_publicacion": parse_date(conv_data.get("fechaPublicacion")),
            "fecha_inicio_solicitud": parse_date(conv_data.get("fechaInicio")),
            "fecha_fin_solicitud": parse_date(conv_data.get("fechaFin")),
            "finalidad_id": conv_data.get("finalidad", {}).get("id"),
            "finalidad_nombre": conv_data.get("finalidad", {}).get("nombre"),
            "region_id": conv_data.get("region", {}).get("id"),
            "region_nombre": conv_data.get("region", {}).get("nombre"),
            "organo_convocante": conv_data.get("organo", {}).get("nombre"),
            "tipo_administracion": conv_data.get("tipoAdministracion"),
            "presupuesto_total": conv_data.get("presupuesto"),
            "url_bdns": f"https://www.infosubvenciones.es/bdnstrans/GE/es/convocatoria/{conv_data.get('numeroConvocatoria')}",
            "tipos_beneficiario": conv_data.get("tiposBeneficiario", []),
        }
        
        return parsed
