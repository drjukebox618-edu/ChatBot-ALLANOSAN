"""
Processador de imagens otimizado.
Sistema enxuto para OCR e análise de imagens.
"""
import os
import io
import base64
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from PyQt6.QtWidgets import QFileDialog, QApplication

# OCR opcional
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# PDF opcional
try:
    from pdf2image import convert_from_path
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from src.core.gemini_api import GeminiAPI
from src.utils.decorators import log_performance
from src.config.settings import IMAGE_SUPPORTED_FORMATS, IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)
@dataclass
class ImageAnalysis:
    """Resultado de análise de imagem."""
    description: str
    ocr_text: str = ""
    confidence: float = 0.0
    format: str = ""
    size: Tuple[int, int] = (0, 0)
    file_size: int = 0
class OCRProcessor:
    """Processador OCR otimizado."""
    
    def __init__(self):
        self.available = OCR_AVAILABLE
        if not self.available:
            logger.warning("OCR indisponível. Instale: pip install pytesseract")
    
    def extract_text(self, image_path: str) -> str:
        """Extrai texto da imagem."""
        if not self.available:
            return ""
        
        try:
            # Pré-processar imagem para melhor OCR
            with Image.open(image_path) as img:
                # Converter para RGB se necessário
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Melhorar contraste
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                
                # Aplicar filtro para reduzir ruído
                img = img.filter(ImageFilter.MedianFilter())
                
                # Extrair texto
                text = pytesseract.image_to_string(img, lang='por+eng')
                return text.strip()
                
        except Exception as e:
            logger.warning(f"Erro no OCR: {e}")
            return ""
class ImageOptimizer:
    """Otimizador de imagens."""
    
    @staticmethod
    def optimize_for_analysis(image_path: str) -> str:
        """Otimiza imagem para análise."""
        try:
            temp_path = f"{image_path}_optimized.jpg"
            
            with Image.open(image_path) as img:
                # Redimensionar se muito grande
                max_size = 1024
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Converter para RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Salvar otimizado
                img.save(temp_path, 'JPEG', quality=85, optimize=True)
                return temp_path
                
        except Exception as e:
            logger.warning(f"Erro ao otimizar imagem: {e}")
            return image_path
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """Obtém informações da imagem."""
        try:
            with Image.open(image_path) as img:
                file_size = os.path.getsize(image_path)
                return {
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'file_size': file_size
                }
        except Exception as e:
            logger.warning(f"Erro ao obter info da imagem: {e}")
            return {}
class PDFProcessor:
    """Processador de PDFs."""
    
    def __init__(self):
        self.available = PDF_AVAILABLE
        if not self.available:
            logger.warning("PDF indisponível. Instale: pip install pdf2image")
    
    def convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """Converte PDF em imagens."""
        if not self.available:
            return []
        
        try:
            images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=5)
            image_paths = []
            
            base_name = Path(pdf_path).stem
            for i, image in enumerate(images):
                img_path = f"{base_name}_page_{i+1}.jpg"
                image.save(img_path, 'JPEG')
                image_paths.append(img_path)
            
            return image_paths
            
        except Exception as e:
            logger.error(f"Erro ao converter PDF: {e}")
            return []
class ImageProcessor:
    """Processador principal de imagens."""
    
    def __init__(self):
        self.gemini_api = GeminiAPI()
        self.ocr_processor = OCRProcessor()
        self.optimizer = ImageOptimizer()
        self.pdf_processor = PDFProcessor()
    
    @log_performance
    async def process_image_async(self, image_path: str) -> str:
        """Processa imagem de forma assíncrona."""
        try:
            # Verificar se arquivo existe
            if not os.path.exists(image_path):
                return f"Erro: Arquivo não encontrado: {image_path}"
            
            # Obter informações da imagem
            img_info = self.optimizer.get_image_info(image_path)
            if not img_info:
                return "Erro: Formato de imagem não suportado"
            
            # Otimizar imagem
            optimized_path = self.optimizer.optimize_for_analysis(image_path)
            
            # Executar OCR em paralelo com análise visual
            ocr_task = asyncio.create_task(self._extract_text_async(optimized_path))
            analysis_task = asyncio.create_task(self._analyze_with_gemini_async(optimized_path))
            
            ocr_text, visual_analysis = await asyncio.gather(ocr_task, analysis_task)
            
            # Combinar resultados
            result = self._combine_results(visual_analysis, ocr_text, img_info)
            
            # Limpar arquivo temporário se foi criado
            if optimized_path != image_path and os.path.exists(optimized_path):
                os.remove(optimized_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return f"Erro no processamento: {str(e)}"
    
    async def _extract_text_async(self, image_path: str) -> str:
        """Extração de texto assíncrona."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.ocr_processor.extract_text, image_path)
    
    async def _analyze_with_gemini_async(self, image_path: str) -> str:
        """Análise visual assíncrona."""
        try:
            response = await self.gemini_api.send_message_with_image_async(
                image_path, IMAGE_ANALYSIS_PROMPT
            )
            return response.get('text', 'Erro na análise visual')
        except Exception as e:
            logger.warning(f"Erro na análise visual: {e}")
            return "Análise visual indisponível"
    
    def _combine_results(self, visual_analysis: str, ocr_text: str, img_info: Dict) -> str:
        """Combina resultados da análise."""
        result_parts = []
        
        # Análise visual
        if visual_analysis and "erro" not in visual_analysis.lower():
            result_parts.append(f"📸 Análise Visual:\n{visual_analysis}")
        
        # Texto extraído
        if ocr_text:
            result_parts.append(f"📝 Texto Extraído:\n{ocr_text}")
        
        # Informações técnicas
        if img_info:
            size_mb = img_info.get('file_size', 0) / (1024 * 1024)
            tech_info = (
                f"ℹ️ Informações Técnicas:\n"
                f"Formato: {img_info.get('format', 'Desconhecido')}\n"
                f"Dimensões: {img_info.get('size', (0, 0))[0]}x{img_info.get('size', (0, 0))[1]}\n"
                f"Tamanho: {size_mb:.1f} MB"
            )
            result_parts.append(tech_info)
        
        return "\n\n".join(result_parts) if result_parts else "Nenhuma informação extraída"
    
    def process_image(self, image_path: str) -> str:
        """Versão síncrona do processamento."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_image_async(image_path))
    
    def select_image_file(self) -> Optional[str]:
        """Abre diálogo para seleção de imagem."""
        try:
            if not QApplication.instance():
                return None
            
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Selecionar Imagem",
                "",
                "Imagens (*.jpg *.jpeg *.png *.bmp *.gif *.tiff);;Todos os arquivos (*)"
            )
            
            return file_path if file_path else None
            
        except Exception as e:
            logger.error(f"Erro ao selecionar arquivo: {e}")
            return None
    
    def is_supported_format(self, file_path: str) -> bool:
        """Verifica se formato é suportado."""
        try:
            extension = Path(file_path).suffix.lower()
            return extension in IMAGE_SUPPORTED_FORMATS
        except:
            return False
    
    def batch_process_images(self, image_paths: List[str]) -> Dict[str, str]:
        """Processa múltiplas imagens."""
        results = {}
        
        for path in image_paths:
            if self.is_supported_format(path):
                try:
                    result = self.process_image(path)
                    results[path] = result
                except Exception as e:
                    results[path] = f"Erro: {str(e)}"
            else:
                results[path] = "Formato não suportado"
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Status do processador."""
        return {
            'ocr_available': self.ocr_processor.available,
            'pdf_available': self.pdf_processor.available,
            'gemini_connected': bool(self.gemini_api.client),
            'supported_formats': IMAGE_SUPPORTED_FORMATS
        }
