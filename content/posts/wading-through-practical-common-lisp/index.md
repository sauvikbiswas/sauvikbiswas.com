---
title: "Wading through Practical Common Lisp"
date: 2014-07-10
categories: 
  - "coding"
tags: 
  - "lisp"
  - "peter-seibel"
  - "practical-common-lisp"
---

About six months ago, I had this sudden urge to learn a new computer language. Over the years I have learned more than half a dozen languages and used them to solve various kinds of problems. I can grasp the fundamentals of a language pretty quickly - mostly owing to some level of abstraction and correspondence with a known language.

After reading [this](http://norvig.com/21-days.html) and [this](http://www.catb.org/~esr/faqs/hacker-howto.html), I was convinced Lisp was the way to go. In the last year I have tried working my way through MIT Scheme, Racket, and even [Lisp Games](http://www.amazon.com/Land-Lisp-Learn-Program-Game/dp/1593272812) - each to a different degree of utility and completion. Sadly, I was not able to get anything out of these.

I realised much later that the basic entry point that I had chosen was wrong. I prefer knowing mechanisms more than syntax. The books and the tutorials I was referring to were more aimed at solving direct problems. While it is fun to write things that work, it is extremely important to know why exactly does it work.

![](51g27H8RUCL.jpg)

Enter Peter Seibel and [Practical Common Lisp](http://www.amazon.com/Practical-Common-Lisp-Peter-Seibel/dp/1590592395/ref=pd_sim_b_7?ie=UTF8&refRID=0MDGNNBK05NE2138XWR6). (For those short on cash can avail the [online free version](http://www.gigamonkeys.com/book)). The text is a joy to read. I enjoy his elaborate footnotes. ON top of that it took me four sittings to wade through the third chapter. Compared to [Learn Python the Hard Way](http://learnpythonthehardway.org/book/), this was like snail's pace. Three years ago, when I started learning Python, I was sailing through four or five chapters in one sitting.

There are a few things that I liked about the approach. Peter Seibel asks the reader to use SLIME+CCL combo found in lispbox. This makes things pretty coherent and consistent. Most Lisp implementations have customisations (macros?) defined on top of the ANSI standard. For a newbie like me, it was necessary that the author uses a lower level standard construct. As I improve my understanding and start working on problems on my own, I would eventually discover them anyways.

He introduced the symbol types early on. That was a big relief. Often while attempting to understand a form, I re-read the earlier chapters. This has been of great help.

Right now I am at chapter 8 - defining macros of my own. There are many new things that I am being exposed to. That's why, I am taking it slow.
