"""mini URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.contrib import admin
from douban import views

urlpatterns = [
    url(r'^index$', views.index),
    url(r'^movie$', views.movie),
    url(r'^asset_show_table', views.show_asset_in_table, name='show_asset_in_table'),
    url(r'^image_show', views.image_show, name='image_show'),
    url(r'^image_detail', views.image_detail, name='image_detail'),
    url(r'^spider', views.spider, name='pider'),
    url(r'^start_spider', views.start_spider, name='start_spider'),
    url(r'^stop_spider', views.stop_spider, name='stop_spider'),
]
