---
title: "Experimenting with Flask micro-framework"
date: 2017-01-22
categories: 
  - "coding"
tags: 
  - "django"
  - "flask"
  - "ninjin"
  - "python"
  - "rails"
coverImage: "Flask-logo.sh_.png"
---

A few months ago, I had asked Mogit if we can up with a simple collaboration system similar to [Basecamp](https://basecamp.com/). The objective was not only to come-up with a set of tools that we could use ourselves but also learn the newer tricks-of-the-trade. Let's face it, the last time I had programmed any real website was in 2007; and compared to any piece of code in a modern scripting language, my old codes in PHP look really ugly.

A quick search revealed that the two most preferred frameworks for writing modern web applications are [Rails](http://rubyonrails.org/) and [Django](https://www.djangoproject.com/). These are frameworks that are built on Ruby and Python respectively. Although neither is better than the other, fanboys of either of these languages usually stick to whatever is closer to their home. Incidentally, Rails (or Ruby on Rails / RoR) has been developed by David Heinemeier Hansson (DHH). The whole framework emerged as a side-effect of building Basecamp. Basecamp itself was a side-effect of an attempt to organise the multitude of projects that were picked up by the company (known as 37 signals back then).

{{< iframe "https://www.youtube.com/embed/sb2xzeWf-PM" "560" "315" >}}

I gravitated towards Django because I am familiar with Python. I use Python regularly at my workplace to automate procedures. On the other hand, I have not even written a single line of Ruby code till date.

## The fundamental problem of Django (or Rails)

I can concisely say why Django framework must not be used by beginners - it is heavy. While I agree that, for someone who is well versed with Django, creating a file and folder structure with boilerplate code to start off on a project can be real easy, but those who are new to the framework would struggle with the multitude of configuration files and code containing nothing but setup information. It is just like learning a new language. One must learn the syntax before they can even write a simple program; and then, in order to write elegant and efficient programs in that language, one must internalise the concepts of the language.

This paradigm extends itself well to frameworks, APIs, bindings, etc. Every framework has a design principle -  a fundamental way in which the author has intended the framework to be used. This is a long and arduous journey. And walking that path, only to use a few of the sub-systems, is not a very efficient method to write an application if one is hard-pressed on time.

A few months ago, I had sat down and completed [this entire tutorial](https://docs.djangoproject.com/en/1.10/intro/tutorial01/) in Django. It took me a lot of time. In the end I realised that modules are very tightly coupled, there is too much code for setting up the application and the learning curve is steep.

## A micro-framework that does very little

![](flask-768x301.png)

The solution to this problem came out of a few answers on Quora and some replies on StackExchange. [Flask](http://flask.pocoo.org/) seemed to be the choice of many. (In fact, many had suggested [Sinatra](http://www.sinatrarb.com/) over Rails for the exact same reasons.)

I packed my laptop and landed in front of Mogit's house. I suggested that we sit for a few hours and get a system and backbone ready. We both dove into Flask's simple tutorials and started churning out segments after segments of disjoint functionalities. Since Flask has very low overhead, we had to separately install a MySQL binding and some Markup/Markdown packages. It wasn't a big deal since most of the code _did_ stuff instead of managing configurations.

I loved the Jinja2 templating engine built-into the framework. It was very simple to churn out two or three templates that covered most of out needs for the time being. It ensured that we had an interface to enter and retrieve data that (badly) simulated a discussion forum and a to-do list. In roughly eight hours spread over yesterday evening and today morning, we had more functionalities than our code appeared to have.

Let's face it, even we weren't sure of what we were trying to make.

\[caption id="attachment\_2749" align="alignnone" width="640"\][![](Gecko-Syrup-PiratasdoCapitoUsopp1.jpg)](http://sauvikbiswas.com/wp-content/uploads/2017/01/Gecko-Syrup-PiratasdoCapitoUsopp1.jpg) Usopp Pirates\[/caption\]
