from utils import normalize_text, smart_trim

async def analyze_text(text: str) -> dict:
    text = smart_trim(normalize_text(text))

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={"type": "json_object"},
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
        )

        # Extract dict directly
        output_data = None
        for item in response.output:
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    output_data = block.get("text")  # already dict

        if not output_data:
            raise ValueError("No JSON output")

        # Use it directly
        intent = output_data.get("intent")
        confidence = output_data.get("confidence")
        signals = output_data.get("signals", [])

        if intent not in VALID_INTENTS:
            raise ValueError("Invalid intent")

        if not isinstance(confidence, int):
            confidence = 0  # fallback

        confidence = max(0, min(confidence, 100))

        if not isinstance(signals, list):
            signals = []

        return {
            "intent": intent,
            "confidence": confidence,
            "signals": signals[:5]
        }

    except Exception:
        return {
            "intent": "legit",
            "confidence": 0,
            "signals": ["NLP unavailable"]
        }
