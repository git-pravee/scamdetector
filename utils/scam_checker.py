def detect_scam(text):
    scam_keywords = [
        "registration fee", "pay to apply", "quick money", "earn ₹50000", 
        "WhatsApp only", "no skills required", "easy income", "limited slots"
    ]
    text = text.lower()
    for keyword in scam_keywords:
        if keyword in text:
            return "⚠️ Warning: This job description contains scam indicators."
    return "✅ This job description looks safe."
