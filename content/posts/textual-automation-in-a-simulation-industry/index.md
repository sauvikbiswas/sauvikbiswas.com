---
title: "Textual automation in a simulation industry"
date: 2014-03-16
categories: 
  - "coding"
tags: 
  - "automation"
  - "coding-2"
  - "workplace"
---

_The following piece of writing originally appeared on my earlier blog._

I have been observing people lately who do similar work as mine. The core engineering group is highly dependent on simulation of physical problems. All of it is to essentially de-risk actual physical events or worse, to evaluate the root cause of a real world problem. Well, one of the key causes of such kind of work in India can be attributed to the lack of manufacturing units. Our engineering education, no matter how rigorous it may be, on one hand addresses the curriculum from a purely theoretical standpoint, while on the other hand helps create brilliant analysts who can actually shine through jobs that require simulation on a computer. It doesn't mean that the person is incapable of real world engineering. It's just that he has very less opportunities here.

### The toolset of the environment

As of today, I have come across many software that ease the process of creating these models for simulation. There are essentially two types of such software. One that takes the parameters of the model in a text format and can run the required analysis, and another that only allows the user to operate within the proprietary limits of the software itself. Needless to say, unless the latter kind of software exposes any API to let the user tinker with its parameters, any kind of attempt at automation will be futile. Luckily, it is the former group that forms the majority of the environment in which a simulation engineer with Mechanical Engineering background thrives.

Let me clarify a bit about the subset of people I am referring to. These are the engineers who work on structural problems, problems of fluid dynamics and in general static and dynamic physical systems. Often the toolset comprises of the bigger names that serve the foundation of such computation. Say, in the fluid dynamics world, there is Fluent, Star CCM+ and their likes, while in the structural world, there is Ansys, Nastran, Abaqus and their brothers and cousins. These simulators work well with hand written textual inputs that describe the nooks and corners of the model. And indeed, that's how such a software should be. The really good ones also have exposed APIs thus even encroaching the territory of the latter kind of software described in the earlier paragraph.

### What is needed?

In short what one needs is a lexical parser. In fact, the knowledge of a simple language that supports regular expression is what the engineer needs in his arsenal. If there is one thing that he needs to learn it has to be regexp.  Let me put it in a way that would set a pathway for learning. One of the easiest way to deal with this is to work on it using the standard grep program on any \*NIX machine. However I really found this to be a difficult job as many of us have to log into clusters and just getting into something complex for the experimentation kills the drive to have a go at it. One simple alternative is to use a text editor that supports at least basic regexp and start off experimenting with simple find / replace expressions. While Vim, with its availability on both Unix / Linux as well as Windows, is a good idea, it may be a daunting task for a beginner to start working on a purely console based editor\[1\]. One alternative is to use Notepad++ or similar text editor on Windows.

Text editors do have quite a bit of limitations regarding this. I have to admit that the implementation of regexp in text editors is not really exhaustive. Also, most editors really focus on simple find / replace solutions. This is when one has to upgrade to a programming language that has really good support for regexp. Also, it would be beneficial to choose a language that is simpler to code. I have been using Python for it lends well to rapid prototyping. Indeed, any similar scripting language can be used - whatever the user is comfortable with and whatever is available at hand.

Beyond this point, I would be leaving the generics and cite examples of my own approach. Anyone interested can easily extrapolate or morph the information to suit his own needs.

### Parsing text into bits of useful information

The text often follows a pattern and that's a good thing. In my case, the two most frequently used solvers are Nastran and Abaqus. The former has a very rigid syntax while the latter is a bit more human readable. From a lexical coding point of view, I must say, the more rigid the syntax, the better. Indeed, when I had to think about dependent entries laid out in a sequential manner in Abaqus, I was cursing its syntax. This meant that there were keywords that had to be a slave to another keyword and the lexical parser should be able to create master information and slave information. I am quite sure that every solver (in any field) would have its quirks.

Identification of this pattern is only half the battle won. At this point one will have to come up with a framework that can do generic parsing. In my case, it was a labyrinth of classes that threw out a nest of basic data structures - lists, dicts and tuples. One of my colleagues prefers to extract data as custom class objects. I differ with that philosophy. If the data exists as custom class objects, the author will have to write a lot of other methods to extract the data contained in those objects. That is inefficient. It's like extracting randomly scattered data from a box, organising them and putting them in another box. I prefer the organised data straight out of the first box. His methods have their own merits - i.e. if there is an industrial level distributive application being written, I can acknowledge the usefulness and to some extent necessity of such an approach. Then again, here we are talking about the simulation industry where rapid, disposable\[2\], development of code comes more handy.

What we are looking for here is to build a framework with a handful of exposed APIs. These APIs will become the backbone of any disposable application that one intends to build. For example, the framework I use to parse Abaqus files allows me to write complex alterations in only a couple of lines. The most expansive ones does not exceed fifty lines. Of course, the framework took me months to build and contains a few thousand lines. Knowing that those thousand lines will work well in the background, writing disposable programs takes anything from few minutes to at most a few hours.

As a concluding remark, I can say that this is one way of doing things but is not a do all, end all kind of scenario. I am quite sure that there are other ways of textual automation, some more efficient than the others. In case one is totally afraid of writing codes - and I have seen quite a few people - they should be able to do some level of lexical parsing using a modern spreadsheet software.

### Notes:

1\. It would be a good idea to invest some time in learning to use a faster editor like Vim in order to code. Even Emacs will be a good option. Personally, I have a bit bias towards Vim. 2. By "disposable" I mean applications that exist only to solve a problem at hand and may have no importance later - thus negating any merit in storing the application in a cool, dry place.
