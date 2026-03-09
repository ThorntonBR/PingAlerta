import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from status_checker import verificar_servico

# Carrega o token do arquivo .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configura o nível de log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dicionário de serviços que queremos monitorar
SERVICOS = {
    'youtube': 'youtube',
    'netflix': 'netflix',
    'nubank': 'nubank',
    'whatsapp': 'whatsapp',
    'discord': 'discord',
    'correios': 'correios',
    'instagram': 'instagram',
    'facebook': 'facebook',
    'spotify': 'spotify',
    'twitch': 'twitch'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com uma mensagem de boas-vindas."""
    comandos = "\n".join([f"/{cmd} - Verificar {cmd.capitalize()}" for cmd in SERVICOS.keys()])
    mensagem = (
        f"👋 Olá! Sou um bot que verifica a instabilidade de serviços online.\n\n"
        f"Comandos disponíveis:\n{comandos}\n\n"
        f"Exemplo: /nubank\n\n"
        f"Digite /status para ver todos os serviços de uma vez!"
    )
    await update.message.reply_text(mensagem)

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler genérico para comandos de verificação de status.
    """
    comando = update.message.text[1:]  # Remove a barra do comando
    nome_servico = SERVICOS.get(comando)
    
    if not nome_servico:
        await update.message.reply_text(f"Comando /{comando} não reconhecido. Use /start para ver a lista.")
        return
    
    # Envia uma mensagem inicial
    await update.message.reply_text(f"🔍 Verificando status de {comando.capitalize()}...")
    
    try:
        # Chama a função que verifica o status
        resultado = verificar_servico(nome_servico)
        await update.message.reply_text(resultado)
    except Exception as e:
        logger.error(f"Erro ao verificar {nome_servico}: {e}")
        await update.message.reply_text(f"❌ Erro ao verificar {comando.capitalize()}. Tente novamente mais tarde.")

async def status_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica o status de todos os serviços de uma vez"""
    await update.message.reply_text("🔍 Verificando todos os serviços... Isso pode levar alguns segundos.")
    
    resultados = []
    for comando, slug in SERVICOS.items():
        try:
            status = verificar_servico(slug)
            # Pega apenas o emoji e o nome para simplificar
            linhas = status.split('\n')
            if linhas:
                primeira_linha = linhas[0]
                resultados.append(primeira_linha)
        except Exception as e:
            resultados.append(f"❌ {comando.capitalize()}: Erro na verificação")
    
    # Junta todos os resultados em uma única mensagem
    mensagem_final = "📊 **STATUS DOS SERVIÇOS**\n\n" + "\n".join(resultados)
    await update.message.reply_text(mensagem_final)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com erros do bot"""
    logger.error(f"Erro na atualização {update}: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ Ocorreu um erro interno. Tente novamente mais tarde.")

def main():
    """Função principal para iniciar o bot"""
    if not BOT_TOKEN:
        logger.error("Token não encontrado! Certifique-se de que o arquivo .env está configurado.")
        return
    
    try:
        # Cria a aplicação do bot
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Adiciona os handlers
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('status', status_todos))
        
        # Adiciona um handler para cada comando de serviço
        for comando in SERVICOS.keys():
            application.add_handler(CommandHandler(comando, status_handler))
        
        # Adiciona handler de erros
        application.add_error_handler(error_handler)
        
        # Inicia o bot
        logger.info("🚀 Bot iniciado com sucesso!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Erro fatal ao iniciar o bot: {e}")
        raise

if __name__ == '__main__':
    main()