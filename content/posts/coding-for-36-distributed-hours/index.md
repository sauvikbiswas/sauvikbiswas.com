---
title: "Coding for 36 distributed hours"
date: 2017-02-24
categories: 
  - "coding"
tags: 
  - "flask"
  - "ninjin"
  - "python"
coverImage: "Screenshot-2017-02-24-21.30.40.png"
---

About a month ago, [I had worked for three days](/posts/how-useful-can-an-app-made-in-3-days-be/) to come up with a proof of concept for a project collaboration platform aimed at a small company - typically less than 40 people). The webapp was not something that could be actually used by anyone. There were glaring holes and missing functionalities that would be useless for any actual company.

I still had no idea as to how much time would it take to polish it to a point that it would be a commercially viable product.

Here were my objectives:

1. A project (segment) consists of individual discussions.
2. A discussion (thread) consists of individual [Markdown formatted](https://daringfireball.net/projects/markdown/syntax) posts.
3. A post can contain some text or attachments. It can also have some searchable tags.
4. A collection of to-do entry resides inside a project.
5. It is possible to start a discussion thread against a to-do entry.
6. It is possible to mark a discussion as a to-do entry.
7. The author of a discussion thread / to-do can assign the to-do to anyone else.
8. A to-do mark can only be closed either by the author or by the one who has been assigned.
9. The author of a thread can lock the thread.
10. The registration system is not open. Only an admin can invite an user.
11. An admin can grant regular users admin privileges as well as lock their account.
12. The author of a thread can also invite an external user who can only participate in that thread.

One of the biggest problem with my proof of concept was the MySQL interface implementation. It took me quite a few hours of work to write an abstraction layer that can work with people simultaneously accessing different databases. This was necessary as each company is assigned a unique database while everyone would be accessing these databases via the same code. The solution was not to have a persistent connection but create an on demand connection and cursor whenever a request is received.

One weekend, me and Mogit sat down and drew the interfaces on paper. This became the basis for the layout of the webapp. It's fairly simple and looks best on a desktop. The CSS needs a lot of tweaking for mobile and low resolution screens. I can safely say that it is far simpler to transform hand-drawn layouts to their HTML+CSS counterparts than toil somewhat aimlessly on a computer.

Once the overall templates were ready, it was all about writing the implementation. Barring a handful of functions, most of the code has been re-written. Just like any other form of art, churning out simple and efficient application in a framework takes time. This also means that I have a fair idea of how to approach an webapp in [Flask](http://flask.pocoo.org/). Next time, it would be much faster.

We are using Ninjin to develop Ninjin itself. (That's so meta!)

{{< figure src="Screenshot-2017-02-24-21.31.07-e1487952434848.png" caption="Two projects focussed on development and bug tracking respectively." >}}

{{< figure src="Screenshot-2017-02-24-21.30.40.png" caption="Here is a list of stuff that I will have to do before I can call it a _product_." >}}

{{< figure src="Screenshot-2017-02-24-21.34.23-e1487952404690.png" caption="This is what the thread author option looks like." >}}

I had kept a track of the number of hours I had spent behind this project. Not counting the initial three day hackathon, I have spent 36 hours in building this app. That's not bad for a start!
