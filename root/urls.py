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
from articleRec import handler as articleRecHandler
from topicModeling import handler as topicModelHandler
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', articleRecHandler.hello_world),
    path('populateArticles/', articleRecHandler.populate_articles),
    path('queryArticles/', topicModelHandler.query_documents_url),
    path('trainTopicModel/', topicModelHandler.retrain_topic_model),
]

