import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Importa nossa função de verificação de status
from status_checker import verificar_servico

# Carrega o token do arquivo .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configura o nível de log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Dicionário de serviços que queremos monitorar
# A chave é o comando que o usuário vai digitar, o valor é o 'slug' usado no site.
SERVICOS = {
    'youtube': 'youtube',
    'netflix': 'netflix',
    'nubank': 'nubank',
    'whatsapp': 'whatsapp-messenger',  # Às vezes o slug é diferente
    'discord': 'discord',
    'correios': 'correios',
    # Adicione quantos serviços quiser!
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com uma mensagem de boas-vindas."""
    comandos = "\n".join([f"/{cmd} - Verificar {cmd.capitalize()}" for cmd in SERVICOS.keys()])
    mensagem = (
        f"👋 Olá! Sou um bot que verifica a instabilidade de serviços online.\n\n"
        f"Comandos disponíveis:\n{comandos}\n\n"
        f"Exemplo: /nubank"
    )
    await update.message.reply_text(mensagem)

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler genérico para comandos de verificação de status.
    O nome do comando é usado para encontrar o serviço correspondente.
    """
    comando = update.message.text[1:]  # Remove a barra do comando
    nome_servico = SERVICOS.get(comando)
    
    if not nome_servico:
        await update.message.reply_text(f"Comando /{comando} não reconhecido. Use /start para ver a lista.")
        return
    
    # Envia uma mensagem inicial para o usuário saber que o bot está processando
    await update.message.reply_text(f"🔍 Verificando status de {comando.capitalize()}...")
    
    # Chama a função que verifica o status
    resultado = verificar_servico(nome_servico)
    
    # Envia o resultado de volta para o usuário
    await update.message.reply_text(resultado)

if __name__ == '__main__':
    if not BOT_TOKEN:
        raise ValueError("Token não encontrado! Certifique-se de que o arquivo .env está configurado.")
    
    # Cria a aplicação do bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Adiciona o handler para o comando /start
    application.add_handler(CommandHandler('start', start))
    
    # Adiciona um handler para cada comando de serviço
    for comando in SERVICOS.keys():
        application.add_handler(CommandHandler(comando, status_handler))
    
    # Inicia o bot em modo polling (fica ouvindo por novas mensagens)
    print("🤖 Bot iniciado e aguardando comandos...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)