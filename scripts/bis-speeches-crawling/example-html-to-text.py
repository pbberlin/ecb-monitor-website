from bs4 import BeautifulSoup

# your HTML string
htmlContent = """
    <h1>My heading</h1>
    <h2>Subtitle</h2>

    <p>This is a paragraph</p>
    <p>This is a paragraph that ends properly.</p>
"""

# parse with BeautifulSoup
soup = BeautifulSoup(htmlContent, "html.parser")

# define which tags should be checked for sentence delimiter
headerTags = ["h1", "h2", "h3", "h4", "h5", "h6", "p"]

# define which characters count as sentence delimiters
sentenceDelimiters = [".", "!", "?"]

# collect output text pieces
textParts = []

for idx1, tag in enumerate(soup.find_all(headerTags)):
    text = tag.get_text(strip=True)
    if len(text) > 0:
        lastChar = text[-1]
        if lastChar not in sentenceDelimiters:
            text = text + "."
        textParts.append(text)

# join them with newlines
finalText = "\n".join(textParts)

print(finalText)
