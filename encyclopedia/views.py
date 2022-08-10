from django.shortcuts import render
from django.http import HttpResponse
from django import forms


from . import util

import markdown
import random


class SearchForm(forms.Form):
    key_word = forms.CharField(label = "", widget = forms.TextInput(attrs = {'placeholder' : 'Search encyclopedia'}), max_length = 100)


class PageForm(forms.Form):
    title = forms.CharField(label = "", widget = forms.TextInput(attrs = {'placeholder' : 'Title'}), max_length = 100)
    details = forms.CharField(label = "", widget = forms.Textarea(attrs = {'placeholder' : 'Details'}))



def index(request):
    return render(request, "encyclopedia/index.html", {
        "search_form" : SearchForm(),
        "entries": util.list_entries()
    })

def random_page(request):
    title = random.choice(util.list_entries())
    md = util.get_entry(title)
    html_file = markdown.markdown(md)

    return render(request, "encyclopedia/pages.html", {
    "search_form" : SearchForm(),
    "title" : title,
    "body" : html_file
    })



def entry(request, title):
    md = util.get_entry(title)

    if md is not None:
        html_file = markdown.markdown(md)

        return render(request, "encyclopedia/pages.html", {
            "search_form" : SearchForm(),
            "title" : title,
            "body" : html_file
        })
    else:
        return render(request, "encyclopedia/pages.html", {
            "search_form" : SearchForm(),
            "title" : 'Error',
            "body" :  "<h1>The requested page is not available</h1>"
        })




def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            word = form.cleaned_data["key_word"]

            #similar to entry code
            md = util.get_entry(word)
            if md is not None: #word found directly
                html_file = markdown.markdown(md)

                return render(request, "encyclopedia/pages.html", {
                    "search_form" : SearchForm(),
                    "title" : word,
                    "body" : html_file
                })
            else: #find using keyword
                words = []
                for entry in util.list_entries():
                    if word in entry:
                        words.append(entry)


                return render(request, "encyclopedia/search.html", {
                    "search_form" : SearchForm(),
                    "title" : word,
                    "entries" :  words
                })



    else:
        form = SearchForm()

    return render(request, "encyclopedia/index.html", {
        "search_form" : SearchForm(),
        "entries": util.list_entries()
    })




def create(request):
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            details = form.cleaned_data['details']
            #if title already exists, show error message
            if title in util.list_entries():
                return render(request, "encyclopedia/pages.html", {
                    "search_form" : SearchForm(),
                    "title" : 'Error',
                    "body" :  "<h1>The entered title already exists in the database. </h1>"
                })
            else:
                util.save_entry(title, details)
                return render(request, "encyclopedia/pages.html", {
                    "search_form" : SearchForm(),
                    "title" : title,
                    "body" : details
                })



    else:
        form = PageForm()

    return render(request, "encyclopedia/handle.html", {
        "title" : "Create New Page",
        "edit" : False,
        "search_form" : SearchForm(),
        "page_form" : form
    })




def edit(request, old_title):
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data['title']
            new_details = form.cleaned_data['details']
            util.save_entry(new_title, new_details)
            util.delete_entry(old_title)
            return render(request, "encyclopedia/pages.html", {
                "search_form" : SearchForm(),
                "title" : new_title,
                "body" : new_details
            })

    else:
        old_details = util.get_entry(old_title)
        initial_dict = {"title" : old_title, "details" : old_details}
        form = PageForm(initial = initial_dict)

    return render(request, "encyclopedia/handle.html", {
            "title" : old_title,
            "page_form" : form,
            "edit" : True ,
            "search_form" : SearchForm(),

        })
