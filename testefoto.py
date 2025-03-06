import os
import base64

from io import BytesIO
from PIL import Image

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")

# Configurar o modelo de visão
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=KEY_API)

# Carregar e processar a imagem
pil_image = Image.open("WhatsApp Image 2025-03-03 at 21.25.02.jpeg")

# Converter para base64
image_bytes = BytesIO()
pil_image.save(image_bytes, format="JPEG")
image_str = base64.b64encode(image_bytes.getvalue()).decode("utf-8")

# Criar a mensagem com prompt e imagem
message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": "Transcreva os textos da imagem mantendo suas formatações. Não faça comentários ou frases de conversação com o usuário.",
        },
        {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_str}"
        },
    ]
)

# Chamar o modelo
response = llm.invoke([message])
print(response.content)