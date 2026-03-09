import cloudscraper
from bs4 import BeautifulSoup
import logging

# Configura um logger básico para vermos erros, se houverem
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# O site que vamos consultar (uma alternativa gratuita ao Downdetector)
BASE_URL = "https://istheservicedown.com.br/status/{}"

def verificar_servico(nome_servico: str) -> str:
    """
    Verifica o status de um serviço no site istheservicedown.com.br.
    
    Args:
        nome_servico: O nome (slug) do serviço (ex: 'youtube', 'nubank').
    
    Returns:
        Uma string descrevendo o status do serviço.
    """
    scraper = cloudscraper.create_scraper()
    url = BASE_URL.format(nome_servico)
    
    try:
        logger.info(f"Acessando {url}...")
        response = scraper.get(url, timeout=10)
        response.raise_for_status()  # Levanta um erro se a requisição falhou (ex: 404)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        
        # Palavras-chave que indicam o status (baseado no site escolhido)
        if "nenhum problema detectado" in page_text:
            return f"✅ {nome_servico.capitalize()} - Tudo estável. Nenhum problema detectado."
        elif "alguns problemas detectados" in page_text:
            return f"⚠️ {nome_servico.capitalize()} - Instabilidade parcial. Alguns usuários estão relatando problemas."
        elif "problemas detectados" in page_text or "enfrentando interrupções" in page_text:
            return f"🚨 {nome_servico.capitalize()} - FORA DO AR! Problemas graves detectados."
        else:
            return f"❓ {nome_servico.capitalize()} - Status não pôde ser interpretado no momento."
            
    except cloudscraper.exceptions.CloudflareChallengeError:
        logger.error(f"Erro de Cloudflare ao acessar {url}")
        return f"⚠️ Não foi possível verificar {nome_servico.capitalize()} devido a proteções do site."
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar {nome_servico.capitalize()}: {e}")
        return f"❌ Erro ao verificar {nome_servico.capitalize()}. O serviço existe?"