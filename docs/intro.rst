Introduction
============
Many projects implicitly build pipelines while implementing larger goals eg scraping the web, transforming data, rendering final outputs, or responding to an HTTP request. This project aims to make a reusable set of tools for building these pipelines explicitly.

Goals
-----
1. Inter-project common **code reuse**.
2. **Application code readability**. A high level understanding of an application or module should be clear from reviewing its pipeline and how data moves through the system.
3. **Development tooling**

  - Testing small manageable stages
  - Exception handling
  - Stage timeout, retries, and failures
  - Concurrency whether async io, multi-core, multi-process, or multi-cluster
  - Pausing (checkpointing) the pipeline and restarting
  - Measurement collection and visualization to diagnose bottlenecks

4. **Simple internal structure**. If something is difficult to implement, you're probably doing it wrong or doing the wrong thing.

Status
------
The project is currently in an experimental phase. Work alternates
between  focusing on new features in the API and building out new
example applications to push the API to its limits.

References
----------
Some background history and theory.

* 1930s: Alonzo Church `Lambda Calculus <https://en.wikipedia.org/wiki/Lambda_calculus>`_
* 1950s: John McCarthy, Lisp, and `functional programming <https://en.wikipedia.org/wiki/Functional_programming>`_
* 1973: Douglas McIlroy at Bell Labs and the `Unix pipe <https://en.wikipedia.org/wiki/Pipeline_(Unix)>`_
* 1994: `Chain of responsibility <https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern>`_ pattern from the Design Patterns: Elements of Reusable Object-Oriented Software
* 2010: Julien Palard's `Pipe <https://github.com/JulienPalard/Pipe>`_ Python library. An interesting approach combining overloading the pipe operator | and method chaining to create an infix notation. The library also provides a number of pipe operation primitives.
* 2012: Miner & Shoook's `MapReduce Design Pattern <https://books.google.com/books?id=AAWa8QqCSZwC>`_
* 2014: C++ `RaftLib library <https://en.wikipedia.org/wiki/RaftLib>`_ for distributed pipeline protramming using iostream operators.
* 2015: Martin Fowler's `Collection Pipeline <https://martinfowler.com/articles/collection-pipeline/>`_ article
* Other workflow and streaming projects include: Airflow, SparkStreaming, Oozie
* Python standard libraries like functools and itertools
* `The Iteratee model <https://en.wikipedia.org/wiki/Iteratee>`_ from functional programming is an example of an alternative design pattern.
* Visualization of flow via an `Orr Diagram <https://en.wikipedia.org/wiki/Warnier/Orr_diagram>`_
* `Flow based programming <https://en.wikipedia.org/wiki/Flow-based_programming>`_
* As a solution to the producer / consumer problem.
