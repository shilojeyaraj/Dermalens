from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")
old = "        if not result[\"success\"]:\r\n            raise HTTPException(status_code=500, detail=result[\"error\"])\r\n        \r\n        return {\"message\": \"Profile updated successfully\", \"profile\": result[\"data\"]}"
new = "        if not result[\"success\"]:\n            raise HTTPException(status_code=500, detail=result[\"error\"])\n\n        profile = normalize_user_profile(result.get(\"data\"))\n        return {\"message\": \"Profile updated successfully\", \"profile\": profile}"
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
