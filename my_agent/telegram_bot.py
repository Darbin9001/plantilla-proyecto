import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from my_agent.agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv("TELEGRAM_TOKEN")

# Crear el runner una sola vez al inicio
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent, 
    session_service=session_service,
    app_name='telegram_bot'
)

# Diccionario para mantener sesiones por usuario de Telegram
user_sessions = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    print(f"📩 Mensaje de {user_id}: {user_message}")

    try:
        # Obtener o crear sesión para este usuario
        if user_id not in user_sessions:
            session = await session_service.create_session(
                app_name='telegram_bot',
                user_id=user_id,
                session_id=f'session_{user_id}'
            )
            user_sessions[user_id] = session.id
        
        session_id = user_sessions[user_id]
        
        # Crear el contenido del mensaje del usuario
        message = types.Content(
            role='user',
            parts=[types.Part(text=user_message)]
        )
        
        # Ejecutar el agente con el runner
        response_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            print(f"🔍 Event: {type(event).__name__}")
            
            # Capturar la respuesta final
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
        
        if not response_text:
            response_text = "No pude generar una respuesta."
        
        print(f"🤖 Respuesta: {response_text[:100]}...")
        await update.message.reply_text(response_text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text("Ocurrió un error al procesar tu mensaje.")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Falta el token de Telegram en la variable TELEGRAM_TOKEN")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot de Telegram conectado y esperando mensajes...")
    app.run_polling()