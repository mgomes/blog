Date: May 21, 2018
Tags: chatbots, open source, projects

# Introducing Stealth

After eight months of development, I'm excited to announce the official launch of [Stealth](https://hellostealth.org). Stealth is an open source Ruby framework for creating conversational voice and text chatbots.

Back in August 2017, [Matthew Black](https://whoisblackops.com) and I started imagining a better way to build chatbots. We wanted a framework that included:

* **Support for any messaging service**. If a service wasn’t yet supported, it shouldn’t be difficult to add it in.
* **Support for the all of the great NLP/NLU tools being released**. Again, if one wasn’t supported, it should be easy to add in.
* **Use your own code editor**. The ability to create chatbots using your favorite code editor.
* **Easy handling of common scenarios**. For example, chatbots will sometimes fail to understand users and so handling those scenarios should be baked in (we call them Catch Alls).
* **Deployable anywhere**. We should be able to take advantage of all the great cloud services available.
* **Open source**. We believe deeply that all frameworks and databases should be open source.
* **Support for popular databases**. We wanted to use the great SQL and NoSQL databases that are already available.
* **Support for developer tooling**. We wanted to use continuous integration services like CircleCI and Travis, GitHub, Heroku Pipelines, etc.
* **Testing**. If chatbots are to become first class pieces of software, they need to have testing built-in.

With all of those goals in mind, we decided to create an open source, Ruby framework. We chose the Ruby language not only because it’s our favorite, but also because of the diverse community and rich libraries (gems) available. We even modeled a lot of Stealth around [Ruby on Rails](http://rubyonrails.org).

In addition to all of the great things already provided by Ruby and Rails (ActiveRecord, ActiveSupport, Sidekiq, Sinatra, RSpec, Bundler, wide support, etc.) we also added a few specific things that make building Ruby chatbots with Stealth fun and easy.

Since Stealth is an MVC-architected framework, we had to design our own View layer. We call them [Replies](https://hellostealth.org/docs/#replies). Replies are YAML templates that support ERB. Regardless of which messaging platform your bot is connected to, replies are standardized. This means that connecting your bot to a new network can be as trivial as adding a new gem.

We also built our own concept of [sessions](https://hellostealth.org/docs/#sessions). Sessions in Stealth are Redis-backed and they map users to positions within your bot. We call those positions *flows* and *states*. You can think of flows and states as lightweight state machines. More info about both are in our [Getting Started](https://hellostealth.org/docs/#the_basics.flows) guide.

Lastly, we designed best practices right into the framework. By default, bots come with three flows: **Hello**, **Goodbye**, and **CatchAll**. The *hello* and *goodbye* flows handle user entrances and exits. The *catch_all* flow is responsible for errors and for the times your bot fails to comprehend a user’s message. You can think of the *catch_all* flow as our advanced version of the `HTTP 500` error page. The `catch_all` flow is capable of re-asking questions, routing users to different flows, and even handing off a conversation to a human operator. More info about `catch_all`’s can be found [in our documentation](https://hellostealth.org/docs/#catch_all).

We are releasing [version 1.0](https://github.com/hellostealth/stealth) today and it contains support for everything mentioned above. Additionally, version 1.0 comes with official support for Facebook Messenger and SMS (via Twilio). It also supports [Mixpanel](https://mixpanel.com) analytics and the [AWS Comprehend](https://aws.amazon.com/comprehend/) NLP/NLU service.

We hope you love building chatbots with Stealth, and we can’t wait to see what you build. We already have so many more features and service integrations planned, but we welcome your feedback and pull requests! 🤖
