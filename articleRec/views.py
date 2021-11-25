from .models import ArticleModel
from rest_framework import generics
from .serializers import ArticleSerializer


class ArticleCreate(generics.CreateAPIView):
  # API endpoint that allows you to create an article
  queryset = ArticleModel.objects.all()
  serializer_class = ArticleSerializer

class ArticleList(generics.ListAPIView):
  queryset = ArticleModel.objects.all()
  serializer_class = ArticleSerializer

class ArticleDetail(generics.RetrieveAPIView):
    # API endpoint that returns a single article by pk.
    queryset = ArticleModel.objects.all()
    serializer_class = ArticleSerializer

class ArticleUpdate(generics.RetrieveUpdateAPIView):
    # API endpoint that allows an article record to be updated.
    queryset = ArticleModel.objects.all()
    serializer_class = ArticleSerializer

class ArticleDelete(generics.RetrieveDestroyAPIView):
    # API endpoint that allows an article record to be deleted.
    queryset = ArticleModel.objects.all()
    serializer_class = ArticleSerializer

