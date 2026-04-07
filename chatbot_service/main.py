"""
E-Commerce AI Chatbot Service - Main FastAPI Application.
Combines: RAG (Knowledge Base) + Behavior Model + Google Gemini LLM
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
# === [THAY ĐỔI] Import Groq SDK thay vì Google GenAI ===
from groq import Groq
import asyncio

from knowledge_base import build_context, search_products
from behavior_model import get_behavior_model

# === [THAY ĐỔI] Cấu hình Groq API thay vì Google Gemini ===
# Groq cung cấp inference siêu nhanh với các model mã nguồn mở (Llama, Mixtral...)
GROQ_API_KEY = ""
client = Groq(api_key=GROQ_API_KEY)
# Model sử dụng: llama-3.3-70b-versatile (miễn phí trên Groq, rất mạnh)
GROQ_MODEL = "llama-3.3-70b-versatile"

# === FastAPI App ===
app = FastAPI(
    title="E-Commerce AI Chatbot",
    description="Hệ thống tư vấn khách hàng sử dụng RAG + Deep Learning Behavior Model + Google Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Chat History (in-memory per session) ===
chat_sessions: dict = {}

SYSTEM_PROMPT = """Bạn là Nova AI - trợ lý tư vấn bán hàng của cửa hàng Nova Electronics chuyên Laptop và Điện thoại.

NGUYÊN TẮC:
- Trả lời bằng tiếng Việt, thân thiện, chuyên nghiệp
- Tư vấn dựa trên thông tin sản phẩm và chính sách được cung cấp
- Nếu khách hỏi ngoài phạm vi sản phẩm, hãy lịch sự từ chối và hướng dẫn lại
- Luôn đề xuất sản phẩm phù hợp với nhu cầu khách hàng
- Trả lời ngắn gọn, tối đa 200 từ
"""


# === Request/Response Models ===
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    answer: str
    behavior: dict
    sources: List[str]


class PredictRequest(BaseModel):
    features: Optional[List[float]] = None
    query: Optional[str] = None


# === Endpoints ===
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main RAG chat endpoint."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # 1. Behavior Model - predict customer intent
    bmodel = get_behavior_model()
    behavior = bmodel.predict_from_query(req.message)

    # 2. RAG - retrieve relevant KB context
    kb_context = build_context(req.message)

    # 3. Build prompt with behavior + KB context
    behavior_note = (
        f"[Phân tích hành vi] Khách hàng thuộc nhóm: {behavior['cluster_vi']} "
        f"({behavior['cluster_label']}). Quan tâm: {behavior['focus']}. "
        f"Hãy tư vấn phù hợp với profile này."
    )

    prompt = f"""{SYSTEM_PROMPT}

{behavior_note}

{kb_context}

Lịch sử hội thoại gần đây:
{_get_history(req.session_id)}

Câu hỏi khách hàng: {req.message}

Trả lời tư vấn:"""

    # === [THAY ĐỔI] Gọi Groq API thay vì Google Gemini ===
    answer = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content
            break
        except Exception as e:
            err = str(e)
            if "429" in err and attempt < 2:
                await asyncio.sleep(2 ** attempt * 2)
                continue
            # Fallback: generate answer from KB directly without LLM
            answer = _fallback_answer(req.message, behavior)
            break

    if answer is None:
        answer = _fallback_answer(req.message, behavior)

    # 5. Save to session history
    _save_history(req.session_id, req.message, answer)

    return ChatResponse(
        answer=answer,
        behavior=behavior,
        sources=["knowledge_base/products", "knowledge_base/policies"],
    )


@app.post("/api/predict_intent")
async def predict_intent(req: PredictRequest):
    """Behavior model prediction endpoint."""
    bmodel = get_behavior_model()
    if req.query:
        return bmodel.predict_from_query(req.query)
    elif req.features:
        return bmodel.predict(req.features)
    else:
        raise HTTPException(status_code=400, detail="Provide 'query' or 'features'")


@app.get("/health")
async def health():
    # === [THAY ĐỔI] Cập nhật health check hiển thị đúng LLM đang dùng ===
    return {"status": "healthy", "service": "chatbot-service", "llm": GROQ_MODEL}


# === Helpers ===
def _fallback_answer(query: str, behavior: dict) -> str:
    """Generate a useful answer from KB when Gemini is unavailable."""
    products = search_products(query, top_k=3)
    if not products:
        return "Xin lỗi, em không tìm thấy sản phẩm phù hợp. Anh/chị có thể mô tả rõ hơn nhu cầu không ạ?"

    lines = [f"Dựa trên nhu cầu của anh/chị ({behavior['cluster_vi']}), em xin gợi ý:\n"]
    for i, p in enumerate(products, 1):
        lines.append(f"{i}. **{p['name']}** ({p['brand']}) - ${p['price']}")
        lines.append(f"   {p['description']}")
        lines.append(f"   Thông số: {p['specs']}\n")
    lines.append("Anh/chị quan tâm sản phẩm nào thêm thì cứ hỏi em nhé! 😊")
    return "\n".join(lines)


def _get_history(session_id: str) -> str:
    history = chat_sessions.get(session_id, [])
    if not history:
        return "Chưa có lịch sử."
    lines = []
    for msg in history[-6:]:
        role = "Khách" if msg["role"] == "user" else "Nova AI"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def _save_history(session_id: str, user_msg: str, bot_msg: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({"role": "user", "content": user_msg})
    chat_sessions[session_id].append({"role": "bot", "content": bot_msg})
    if len(chat_sessions[session_id]) > 20:
        chat_sessions[session_id] = chat_sessions[session_id][-20:]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
