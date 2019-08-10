from django.shortcuts import render
from django.http import HttpResponse
from .textSummarizer import extractiveSummarizer,abstractiveSummarizer
# Create your views here.
def index(request):
    return render(request, 'home.htm')

def get_summary(request):
    text = request.POST['data']
    summaryType = request.POST['summaryType']
    if summaryType == 'extractive':
        # extractive is in list format
        extractive = extractiveSummarizer(text)
        return render(request, 'summary.htm', {'extractive' : extractive})
    else:
        abstractive = abstractiveSummarizer(text)
        return render(request, 'summary.htm', {'abstractive' : abstractive})
    