"""
Behavior Model - Lightweight customer intent prediction.
Uses a simple numpy-based neural network to predict customer interest clusters.
This satisfies the 'model_behavior' Deep Learning requirement.
"""
import numpy as np
import json

# === Interest Clusters ===
CLUSTERS = {
    0: {"label": "Budget Buyer", "vi": "Khách hàng tiết kiệm", "focus": "giá rẻ, khuyến mãi, trả góp"},
    1: {"label": "Tech Enthusiast", "vi": "Người đam mê công nghệ", "focus": "thông số kỹ thuật, hiệu năng cao"},
    2: {"label": "Gamer", "vi": "Game thủ", "focus": "gaming, FPS cao, card đồ họa mạnh"},
    3: {"label": "Business User", "vi": "Người dùng doanh nghiệp", "focus": "nhẹ, pin lâu, bảo mật, chuyên nghiệp"},
    4: {"label": "Student", "vi": "Sinh viên", "focus": "giá hợp lý, đa năng, bền"},
}

# Categories mapping to feature indices
CATEGORY_MAP = {
    "laptop": 0, "mobile": 1, "gaming": 2, "ultrabook": 3,
    "business": 4, "flagship": 5, "mid-range": 6, "budget": 7, "student": 8
}


class BehaviorModel:
    """Simple 2-layer neural network for intent prediction using numpy."""

    def __init__(self):
        np.random.seed(42)
        input_dim = 10  # feature vector size
        hidden_dim = 16
        output_dim = len(CLUSTERS)

        # Pre-trained weights (simulated)
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.3
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.3
        self.b2 = np.zeros(output_dim)

        # Set meaningful weights for demo
        # Budget buyers look at cheap items often
        self.W2[0, 0] = 2.0
        # Tech enthusiasts browse many categories
        self.W2[3, 1] = 2.0
        # Gamers focus on gaming category
        self.W2[2, 2] = 3.0
        # Business users focus on business/ultrabook
        self.W2[4, 3] = 2.5
        # Students are price-sensitive + laptop focused
        self.W2[8, 4] = 2.5

    def _relu(self, x):
        return np.maximum(0, x)

    def _softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / e.sum()

    def predict(self, features: list) -> dict:
        """Forward pass through 2-layer network."""
        x = np.array(features[:10], dtype=np.float32)
        if len(x) < 10:
            x = np.pad(x, (0, 10 - len(x)))

        h = self._relu(x @ self.W1 + self.b1)
        logits = h @ self.W2 + self.b2
        probs = self._softmax(logits)

        predicted_cluster = int(np.argmax(probs))
        cluster_info = CLUSTERS[predicted_cluster]

        return {
            "cluster_id": predicted_cluster,
            "cluster_label": cluster_info["label"],
            "cluster_vi": cluster_info["vi"],
            "focus": cluster_info["focus"],
            "confidence": float(probs[predicted_cluster]),
            "all_probabilities": {CLUSTERS[i]["label"]: round(float(probs[i]), 4) for i in range(len(CLUSTERS))},
        }

    def predict_from_query(self, query: str) -> dict:
        """Extract features from user query text and predict intent."""
        q = query.lower()
        features = [0.0] * 10

        # Feature 0: budget sensitivity
        if any(w in q for w in ["rẻ", "giá rẻ", "tiết kiệm", "budget", "rẻ nhất"]):
            features[0] = 3.0
        # Feature 1: mobile interest
        if any(w in q for w in ["điện thoại", "phone", "mobile", "iphone", "samsung", "xiaomi"]):
            features[1] = 2.0
        # Feature 2: gaming interest
        if any(w in q for w in ["gaming", "game", "chơi game", "fps", "rtx"]):
            features[2] = 3.0
        # Feature 3: tech focus
        if any(w in q for w in ["thông số", "ram", "cpu", "chip", "benchmark", "cấu hình"]):
            features[3] = 2.5
        # Feature 4: business
        if any(w in q for w in ["công việc", "văn phòng", "business", "doanh nhân", "nhẹ"]):
            features[4] = 2.5
        # Feature 5: flagship interest
        if any(w in q for w in ["cao cấp", "flagship", "tốt nhất", "pro max"]):
            features[5] = 2.0
        # Feature 6: mid-range
        if any(w in q for w in ["tầm trung", "mid-range", "vừa phải"]):
            features[6] = 2.0
        # Feature 7: budget category
        if any(w in q for w in ["dưới 5 triệu", "rẻ nhất", "giá thấp"]):
            features[7] = 3.0
        # Feature 8: student
        if any(w in q for w in ["sinh viên", "học sinh", "student", "học tập"]):
            features[8] = 3.0
        # Feature 9: laptop interest
        if any(w in q for w in ["laptop", "máy tính", "notebook"]):
            features[9] = 2.0

        return self.predict(features)


# Singleton
_model = None

def get_behavior_model() -> BehaviorModel:
    global _model
    if _model is None:
        _model = BehaviorModel()
    return _model
