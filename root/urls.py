"""ebdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from articleRec import articleApi
from articleRec import views
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', articleApi.hello_world),
    path('populateArticles/', articleApi.fetch_and_hydrate_articles),
    path('createArticle/', views.ArticleCreate.as_view(), name='create-article'),
    path('updateArticle/', views.ArticleUpdate.as_view(), name='update-article'),
    path('deleteArticle/', views.ArticleDelete.as_view(), name='delete-article'),
    path('detailArticle/', views.ArticleDetail.as_view(), name='detail-article'),
    path('listArticles/', views.ArticleList.as_view(), name='list-article'),
]

