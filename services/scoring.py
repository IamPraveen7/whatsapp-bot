def final_score(*scores):
    return min(100, sum(scores))

def classify(score: int):
    if score >= 90:
        return "CRITICAL RISK (almost certainly phishing)"
    if score >= 70:
        return "HIGH RISK (very likely phishing)"
    if score >= 40:
        return "SUSPICIOUS (use caution)"
    return "LOW RISK (no strong phishing signals)"
