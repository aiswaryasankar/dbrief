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
from articleRec import views as articleRecView
from topicModeling import views as topicModelView
from topicFeed import views as topicFeedView
from polarityModel import views as polarityModelView
from passageRetrievalModel import views as passageRetrievalModelView
from homeFeed import views as homeFeedView
from newsletter import views as newsletterView
from userPreferences import views as userPreferencesView

from django.urls import path

urlpatterns = [

    # Admin site
    path('admin/', admin.site.urls),

    # ArticleRec endpoints
    path('home/', articleRecView.hello_world_view),
    path('populateArticles/', articleRecView.populate_articles_batch_view),
    path('populateArticlesV2/', articleRecView.populate_articles_batch_v2_view),
    path('populateArticle/', articleRecView.populate_article_by_url_view),
    path('fetchArticles/', articleRecView.fetch_articles_view),
    path('hydrateArticle/', articleRecView.hydrate_article_view),
    path('articleBackfill/', articleRecView.article_backfill_view),

    #TopicFeed endpoints
    path('getTopicPage/', topicFeedView.get_topic_page_view),
    path('whatsHappening/', topicFeedView.whats_happening_view),

    # TopicModeling endpoints
    path('trainTopicModel/', topicModelView.retrain_topic_model_view),
    path('getDocumentTopic/', topicModelView.get_document_topic_view,),
    path('addDocument/', topicModelView.add_document_view),
    path('queryDocumentsByUrl/', topicModelView.query_documents_url_view),
    path('searchDocumentsByTopic/', topicModelView.search_documents_by_topic_view),
    path('searchTopics/', topicModelView.search_topics_view),
    path('indexDocuments/', topicModelView.index_document_vectors_view),
    path('generateTopicPairs/', topicModelView.generate_topic_pairs_view),

    # TopicModelingV2 endpoints
    # path('trainTopicModelV2/', topicModelView.retrain_topic_model_view_v2),
    # path('getDocumentTopicV2/', topicModelView.get_document_topic_view_v2),
    # path('searchTopicsV2/', topicModelView.search_topics_view_v2),
    # path('getTopicsV2/', topicModelView.get_topics_view_v2),

    # PolarityModel endpoints
    path('getDocumentPolarity/', polarityModelView.get_document_polarity_view),
    path('getDocumentPolarityBatch/', polarityModelView.get_document_polarity_batch_view),

    # PassageRetrievalModel endpoints
    path('getTopPassage/', passageRetrievalModelView.get_top_passage_view),
    path('getFacts/', passageRetrievalModelView.get_facts_view),

    # HomeFeed endpoints
    path('hydrateHomePage/', homeFeedView.hydrate_home_page_view),

    # UserPreferences endpoints
    path('createUser/', userPreferencesView.create_user_view),
    path('getUser/', userPreferencesView.get_user_view),
    path('followTopic/', userPreferencesView.follow_topic_view),
    path('unfollowTopic/', userPreferencesView.unfollow_topic_view),
    path('getRecommendedTopics/', userPreferencesView.get_recommended_topics_for_user_view),
    path('getTopicsYouFollow/', userPreferencesView.get_topics_you_follow_view),

    # Newsletter endpoints
    path('createNewsletterConfig/', newsletterView.create_newsletter_config_for_user_view),
    path('updateNewsletterConfig/', newsletterView.update_newsletter_config_for_user_view),
    path('getNewsletterConfig/', newsletterView.get_newsletter_config_for_user_view),
    path('sendNewsletter/', newsletterView.send_newsletter_view),
    path('sendNewslettersBatch/', newsletterView.send_newsletters_batch_view),
]


