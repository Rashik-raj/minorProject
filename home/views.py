from django.shortcuts import render
from django.http import HttpResponse
from .textSummarizer import extractiveSummarizer,abstractiveSummarizer
# Create your views here.
def index(request):
    return render(request, 'home.htm')

def get_summary(request):
    text = request.POST['data']
    # extractive is in list format
    extractive = extractiveSummarizer(text)
    abstractive = abstractiveSummarizer(text)
    return render(request, 'summary.htm', {'extractive' : extractive, 'abstractive' : abstractive})