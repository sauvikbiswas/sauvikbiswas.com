---
title: "YetiDB: an academic exercise"
date: 2024-02-22
categories: 
  - "coding"
tags: 
  - "database"
  - "yetidb"
coverImage: "C1957B3.jpg"
---

Over the last couple of years I have seen [protobufs](https://protobuf.dev/) being used not only as a means to serialize and deserialize data for transport over network but also as a means to implement a type system, business logic, version control, storage schema, and what not. These often require authoring some sort of custom options (extensions) for the protobuf messages, and writing code that can parse these options and implement some sort of business logic that would use the data contained in the protobuf.

One of the most common usecase is to define storage schema using protobuf. Infobolox's [protoc plugin for GORM](https://github.com/infobloxopen/protoc-gen-gorm) comes to my mind. I have seen being used by many folks, although it is a bit restrictive. One of my teammates wrote his own Python/Jinja-based parser to churn out custom code for our application. Needless to say, he has automated the hell out of our system.

There is always a middle layer that prohibits us from transacting with the database as protobufs. However, if we look at a protobuf's core use case, it is for serializing and deserializing data. This is something that can—in theory—be used for storage and retrieval as well. Most middlewares essentially translate protobufs into language-specific queries. My teammate did it for GORM which in turn generated SQL queries for Postgres, and I did it for generating Cypher queries for neo4j.

Three days ago, I wrote a primary requirement in terms of building a protobuf-centric database—

#### User chooses:

1. A storage system
    1. One Record / File
    
    3. B-Tree based
    
    5. LSM tree
    
    7. Non-indexed sequential

3. A host of servers

#### User interacts with db:

1. Write as protobuf

3. Read into protobuf

It is first-and-foremost an academic exercise. I know very little of how a database really works. This can be an excellent gateway to understanding the fundamentals of a storage system.

There are two books that I will use as my starting point—

1. _Database Internals_ by **Alex Petrov**

3. _Designing Data-Intensive Applications_ by **Martin Kleppmann**

I call it YetiDB. I was reading _Tintin in Tibet_ for the nth time just before I had to give the repository a name. Anyways, here it is—  
[https://github.com/sauvikbiswas/yeti](https://github.com/sauvikbiswas/yeti)

P.S. The answers of [this question](https://softwareengineering.stackexchange.com/questions/121653/create-my-own-database-system) on SoftwareEngineering.StackExchange gave me a lot of confidence.
