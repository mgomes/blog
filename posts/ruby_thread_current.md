Date: December 6, 2018
Tags: ruby, concurrency

# Ruby’s Thread.current

Ruby’s class and instance variables are notorious for their thread safety. While it’s perfectly fine to use class and instance variables within a threaded Ruby application, it’s important to know when doing so will cause issues.

One of the changes I recently made for the release of [Stealth 1.1](https://github.com/hellostealth/stealth) was to move configuration options from a class instance variable to `Thread.current`. Previously, loading a Stealth configuration file looked something like this:

```ruby
def self.config
  @configuration
end

def self.load_services_config
  @semaphore ||= Mutex.new

  @configuration ||= begin
    @semaphore.synchronize do
      # Load config
    end
  end
end
```

As you can see above, the `@configuration` class instance variable is used to store the configuration options. When a Stealth process boots up it parses `services.yml`, stores it in `@configuration`, and thus makes it available to all threads spun up by the process. This worked well for Stealth since it uses Puma and Sidekiq which are both multi-threaded.

One of the design goals for [Mav](https://hiremav.com) is to be able to run a multi-tenant version of Stealth. This means that all customer bots would run on a single Stealth deployment. In order to achieve this, Stealth would need to be able to handle hot-swapping configuration files.

If we were to hot-swap configurations using the class instance variable method above, we would soon run into thread safety issues. To understand why, we have to go through the lifecycle of a Stealth reply:

1. Webhook comes in from a messaging platform (like Facebook Messenger)
2. HTTP request body and headers are pushed into a Sidekiq queue for processing
3. A Sidekiq thread reads the queue, and loads the request body and headers
4. The same Sidekiq thread fires the controller action and crafts a reply by reading the replies folder on disk
5. The same Sidekiq thread transmits the reply back to the messaging platform

Even though Ruby's virtual machine prevents more than one thread from running in parallel for a given process (see [Ruby's GVL](https://www.spacevatican.org/2012/7/5/whos-afraid-of-the-big-bad-lock/)), there is a (likely) chance that the Sidekiq thread above will be paused in Step 4 when it tries to read from disk. Once paused, another thread will be allowed to run.

Now picture a multi-tenant environment where webhooks are flying in and replies flying out.

1. Webhook for `customer 1` comes in from a messaging platform
2. Webhook for `customer 1` is pushed into a Sidekiq queue for processing
3. Sidekiq thread `X` reads the queue, and loads the configuration for `customer 1`
4. Webhook for `customer 2` comes in from a messaging platform
5. Webhook for `customer 2` is pushed into a Sidekiq queue for processing
6. Sidekiq thread `X` fires the controller action and crafts a reply by reading the replies folder on disk
7. Ruby pauses Sidekiq thread `X` and starts thread `Y`
8. Sidekiq thread `Y` reads the queue, and loads the configuration for `customer 2`
9. Sidekiq thread `Y` fires the controller action and crafts a reply by reading the replies folder on disk
10. Ruby pauses Sidekiq thread `Y` and resumes thread `X`
11. Sidekiq thread `X` fires the controller action and crafts a reply by reading the replies folder on disk

It all starts looking a little complicated. But essentially we have two separate webhooks being received before a reply is sent out. In Step 6, we see `thread X` has already loaded the customer's configuration in order to craft its reply. When it requests access to disk, it is paused and `thread Y` is given a chance to run. Since `thread Y` has already loaded `customer 2`'s configuration, when `thread X` is allowed to resume, the `@configuration` variable will now (incorrectly) contain `customer 2`'s information. This is because the class instance variable is shared amongst all threads for the given process.

This is where Ruby's `Thread.current` comes in. While `Thread.current` returns the currently executing thread, it also offers a key-value store that is local to the thread. So for example, if you set `Thread.current[:amazing] = 1`, you would have access to `Thread.current[:amazing]` anywhere within the thread, even after it has been paused and resumed by Ruby.

So we can rewrite our Stealth configuration like this:

```ruby
def self.config
  Thread.current[:configuration]
end

def self.load_services_config
  @semaphore ||= Mutex.new

  Thread.current[:configuration] ||= begin
    @semaphore.synchronize do
      # Load config
    end
  end
end
```

Now each time a thread loads a customer's configuration, it isn't stored at the process level but rather at the thread level. So in Step 11 above, when `thread X` is resumed, it retains access to the configuration options it loaded independently of `thread Y`.

Like with any other global-ish state, it should be used sparingly. Storing too much data in `Thread.current` will make your threads heavy and will slow down Ruby's context switching between them. In this case though, Stealth configurations are fairly small and it's worth the tradeoff.
