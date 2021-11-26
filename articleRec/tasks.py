from background_task import background


# Test background process
@background(queue='my-queue')
def test_background_db_write():

  url="testArticle.com"
  title="testTitile"
  text="testText"
  author="testAuthor"
  publish_date="11-25-2021"
  articleEntry = ArticleModel(
    url = url,
    title = title,
    text = text,
    author = author,
    publish_date = publish_date,
  )
  try:
    articleEntry.save()
  except Exception as e:
    print("Failed to save article in the database")

  print("Background job completed")

test_background_db_write(repeat=5)


