import argparse

from google.cloud import language_v1

def analyze(input):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(content=input, type_=language_v1.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(request={'document': document})

    # Print the results
    return annotations

    # annotations has: .document_sentiment.score, .document_sentiment.magnitude, .sentences, .sentences.score
