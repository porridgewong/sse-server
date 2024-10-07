from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from openai import OpenAI

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()


async def get_llm_response(message: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[{"role": "user", "content": message}],
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {content}\n\n"

    yield "data: [END OF RESPONSE]\n\n"


@app.get("/chat")
async def chat(message: str = None):
    if not message:
        return {"error": "message is required"}

    return StreamingResponse(get_llm_response(message), media_type="text/event-stream")
