import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Load student profiles (adjust path if needed)
with open("knowledge_base/student_profiles.json", "r") as f:
    student_profiles = json.load(f)

# Extract all request types like OPT, CPT, I-20, etc.
all_requests = [
    request["type"]
    for profile in student_profiles
    for request in profile.get("requests", [])
]

# Create a single string for word cloud input
request_text = " ".join(all_requests)

# Generate word cloud
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    colormap='viridis'
).generate(request_text)

# Display the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Word Cloud", fontsize=14)
plt.tight_layout()
plt.show()
