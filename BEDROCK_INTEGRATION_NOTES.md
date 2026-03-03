# Notas de Integración de AWS Bedrock con LangChain

## Información Clave de la Documentación Oficial

### 1. Clases Disponibles

**Para Chat Models (RECOMENDADO):**
- `ChatBedrockConverse` - **Recomendado para la mayoría de casos**
  - Usa la API Converse unificada
  - Soporta streaming
  - Mejor para conversaciones
  - No soporta modelos custom

- `ChatBedrock` - Versión antigua
  - Soporta modelos custom
  - Menos recomendado

- `ChatAnthropicBedrock` - Específico para Anthropic
  - Extiende `ChatAnthropic`
  - Mejor para modelos Claude

**Para Text Completion (NO RECOMENDADO PARA CHAT):**
- `BedrockLLM` - Solo para completación de texto

### 2. Instalación Correcta

```bash
pip install -qU langchain-aws
```

### 3. Configuración de Credenciales

```python
import os

# Opción 1: Variables de entorno (RECOMENDADO)
os.environ["AWS_ACCESS_KEY_ID"] = "your-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret"
os.environ["AWS_SESSION_TOKEN"] = "your-token"  # Si usas credenciales temporales

# Opción 2: Parámetros directos
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    aws_access_key_id="your-key",
    aws_secret_access_key="your-secret",
)
```

### 4. Instantiación Correcta para Chat

```python
from langchain_aws import ChatBedrockConverse

# Para Claude 3.5 Sonnet (RECOMENDADO)
llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    temperature=0.7,
    max_tokens=2000,
)

# Para Claude 3 Sonnet
llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1",
)

# Para Llama 2
llm = ChatBedrockConverse(
    model_id="meta.llama2-70b-chat-v1",
    region_name="us-east-1",
)
```

### 5. Uso con LangChain

```python
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
)

# Uso directo
messages = [
    ("system", "You are a helpful assistant."),
    ("human", "Hello!"),
]
response = llm.invoke(messages)
print(response.content)

# Con prompts
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
])
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.invoke({"input": "What is Python?"})
```

### 6. Streaming

```python
for chunk in llm.stream(messages):
    print(chunk.text, end="", flush=True)
```

### 7. Modelos Soportados

| Modelo | ID | Tipo |
|--------|-----|------|
| Claude 3.5 Sonnet | `anthropic.claude-3-5-sonnet-20240620-v1:0` | Chat |
| Claude 3 Opus | `anthropic.claude-3-opus-20240229-v1:0` | Chat |
| Claude 3 Sonnet | `anthropic.claude-3-sonnet-20240229-v1:0` | Chat |
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | Chat |
| Llama 2 70B | `meta.llama2-70b-chat-v1` | Chat |
| Mistral 7B | `mistral.mistral-7b-instruct-v0:2` | Chat |
| Titan Text Express | `amazon.titan-text-express-v1` | Text |

### 8. Características Soportadas

- ✅ Tool calling (function calling)
- ✅ Structured output
- ✅ Image input
- ✅ Token-level streaming
- ✅ Token usage tracking
- ✅ Extended thinking (Claude models)
- ✅ Prompt caching

### 9. Errores Comunes

**Error:** `AttributeError: 'str' object has no attribute 'get'`
- **Causa:** Usando `ChatBedrock` en lugar de `ChatBedrockConverse`
- **Solución:** Cambiar a `ChatBedrockConverse`

**Error:** `NoCredentialsError`
- **Causa:** Credenciales AWS no configuradas
- **Solución:** Configurar `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`

**Error:** `ModelNotFound`
- **Causa:** Modelo no habilitado en tu cuenta AWS
- **Solución:** Habilitar acceso al modelo en AWS Bedrock console

## Recomendaciones para el Proyecto

1. **Usar `ChatBedrockConverse`** en lugar de `ChatBedrock`
2. **Usar `anthropic.claude-3-5-sonnet-20240620-v1:0`** como modelo por defecto
3. **Configurar credenciales via variables de entorno**
4. **Implementar manejo de errores** para credenciales inválidas
5. **Usar streaming** para mejor UX en conversaciones
6. **Implementar tool calling** para acciones del agente

## Código de Ejemplo Correcto

```python
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

class BedrockAgent:
    def __init__(self):
        self.llm = ChatBedrockConverse(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            region_name="us-east-1",
            temperature=0.7,
            max_tokens=2000,
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful sales agent."),
            ("human", "{input}"),
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
        )
    
    def chat(self, user_input):
        return self.chain.invoke({"input": user_input})
```
