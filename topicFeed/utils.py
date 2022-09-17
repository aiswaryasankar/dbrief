# This file includes extraneous util functions.

def parseSource(url):
  """
    Massive switch condition to tie the url with the source
  """
  source = ""
  if "techcrunch" in url:
    source = "Tech Crunch"
  if "technologyreview" in url:
    source = "Technology Review"
  if "arstechnica" in url:
    source = "Ars Technica"
  if "venturebeat" in url:
    source = "Venture Beat"
  if "vox" in url:
    source = "Vox"
  if "wired" in url:
    source = "Wired"
  if "theverge" in url:
    source = "The Verge"
  if "Ieee" in url:
    source = "IEEE"
  if "cnet" in url:
    source = "CNet"
  if "businessinsider" in url:
    source = "BusinessInsider"
  if "TechSpot" in url:
    source = "Tech Spot"
  if "hackernoon" in url:
    source = "Hacker Noon"
  if "appleinsider" in url:
    source = "Apple Insider"
  if "latimes" in url:
    source = "LA Times"
  if "cnn" in url:
    source = "CNN"
  if "huffpost" in url:
    source = "Huffington Post"
  if "usatoday" in url:
    source = "USA Today"
  if "foxnews" in url:
    source = "Fox News"
  if "breitbart" in url:
    source = "Breitbart"
  if "washingtontimes" in url:
    source = "Washington Times"
  if "thehill" in url:
    source = "The Hill"
  if "apnews" in url:
    source = "AP News"
  if "npr" in url:
    source = "NPR"
  if "nytimes" in url:
    source = "NY Times"
  if "washingtonpost" in url:
    source = "Washington Post"
  if "apnews" in url:
    source = "AP News"
  if "nationalreview" in url:
    source = "National Review"
  if "dj" in url:
    source = "Al Jazeera"
  if "bbc" in url:
    source = "BBC"
  if "politico" in url:
    source = "Politico"
  if "economist" in url:
    source = "Economist"

  return source



