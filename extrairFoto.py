import base64

from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import os
import io
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import HumanMessage
from dotenv import load_dotenv
import tempfile

load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")



def extrair_texto_da_foto(image_bytes):

    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(image_bytes)
    temp_file.close()
    image = temp_file.name

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=KEY_API)

    pil_image = Image.open(image)

    image_bytes = BytesIO()
    pil_image.save(image_bytes, format="JPEG")
    image_str = base64.b64encode(image_bytes.getvalue()).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Transcreva os textos da imagem mantendo suas formatações. Não faça comentários ou frases de conversação com o usuário. Deixe uma formaatação entendivel.",
            },
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{image_str}"
            },
        ]
    )

    # Chamar o modelo
    response = llm.invoke([message])
    return response.content