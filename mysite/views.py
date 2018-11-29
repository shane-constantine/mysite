from django.shortcuts import render_to_response
from read_num.models import get_seven_read_data, get_today_hot_data, get_yesterday_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
import datetime

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_read_data(blog_content_type)
    #获取七天热门博客缓存数据
    seven_hot_data = cache.get('seven_hot_data')
    if seven_hot_data is None:
        seven_hot_data = get_seven_hot_data()
        cache.set('seven_hot_data', seven_hot_data, 3600)
    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['seven_hot_data'] =  seven_hot_data
    return render_to_response('home.html', context)

def get_seven_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=6)
    blogs = Blog.objects \
                             .filter(read_details__date__lte=today, read_details__date__gt=date) \
                             .values('id', 'title') \
                             .annotate(read_num_sum=Sum('read_details__read_num')) \
                             .order_by('-read_num_sum')

    return blogs[:7]