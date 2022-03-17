Date: June 11, 2014
Tags: virtualization, abstraction, innovation

# Levels of Abstraction and Progress

The abstractions we build are the building blocks of future innovations.

{{more}}

Today Google [announced](https://cloudplatform.googleblog.com/2014/06/an-update-on-container-support-on-google-cloud-platform.html) they have added support for [Docker](https://docker.com) in Google App Engine. While this is great news for developers looking for a place to deploy their Docker images, it represents something larger. The Linux container represents a major shift in how we think about servers and the way we interact with them.

If you were to ask a modern web developer to describe the flow of an HTTP request, she would probably tell you:

1. An HTTP request is created by the user’s browser and sent to your server
2. Your server then receives the request through an HTTP server like Apache or Nginx
3. The HTTP server then hands off the request to your application server, something like Puma, Unicorn, Tornado, JBoss, etc

Of course she’s just probably trying to get you to stop asking silly questions and so she glossed over some of the details. If asked to provide details though, most of us would still miss quite a few because they have become abstracted over time.

We often forget that within each HTTP request there are layers upon layers of abstractions as thick as an onion. There are operating systems responsible for wrapping things in a TCP/IP request. There is DNS resolution. There are ethernet or wifi adapters that have drivers and create Ethernet frames. There are routing protocols within your home router and there are routing protocols that that wrap all of that so your request can get routed through datacenters and slowed down by big ISPs.

All of these things must happen for a request to be fulfilled yet we don’t spend much time contemplating them. There was a time when some of these things mattered. We cared about the [brand of our network cards](https://en.wikipedia.org/wiki/3Com), whether the [FreeBSD TCP/IP stack really was really better than Linux](https://arstechnica.com/civis/viewtopic.php?f=16&t=1059599), and we cared about the [hardware our servers ran](https://en.wikipedia.org/wiki/SPARC).

Those things stopped mattering when they all became good enough. We started thinking of them as building blocks we could use to build things. We started using them interchangeably in the systems we build. The abstraction of these components allowed us to focus our efforts higher up the chain.

The same thing is happening to the concept of servers. Virtualization may have started the cycle, but Linux containers are quickly gaining traction for their speed and low overhead.
In addition to Docker support in Google App Engine, Google also announced an open source container cluster management software called [Kubernetes](https://github.com/kubernetes/kubernetes). Earlier this week [Mesosphere](https://mesosphere.com), a commercial version of [Apache Mesos](http://mesos.apache.org) that is used by Twitter to manage their containers, [announced](https://venturebeat.com/2014/06/09/mesosphere-gets-10m-from-andreessen-horowitz-for-data-center-management-tools/) they had closed a $10MM round led by Andreeseen Horowitz.

The abstraction of servers is in full force and I can’t wait until we all describe our infrastructure without even mentioning the word ‘server.’