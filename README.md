# miserly-metrics

A tool to cheaply record key browser metrics (in summary form), like mousemoves,
mouse pauses ("halts"), clicks, etc. Comes complete with JavaScript client, Python Lambda, and MySQL.

Explanations below, but first…

## When is it OK for a product manager to code?

I'm a product manager and a former software engineer. Anyone who has taken that career path knows that you have to monitor and control your own impulses to contribute to the "how" of doing something (architecture, design patterns, code, whatever). Your job is the "what" and "why now". You're to help engineering understand what's the right thing to build (and why); then they own how to build it right.

Now, that does _not_ mean a product manager should never code. 

* Exploring data science or machine learning? **By all means, code away.** Getting your hands dirty is a great way to experience a litle of what ML engineers and doing daily.
* Doing a side project? **Knock yourself out.** Most of the code I write is hobbyist stuff to keep a handful of personal web sites going.
* Need a custom script or SQL to do some number crunching? Transformatons? Image manipulation? Et cetera? **Go for it.** Being able to toss together a quick Python script or SQL query that does something awesome at work is definitely a superpower of a product manager that has tech chops. No one will
* Need something in the product itself but simply don't have room in the roadmap or extra dev capacity to get it done? **_WHOA_** Let's talk about this one.

There's a pretty simple rule: product managers shouldn't write code that goes into a production system. 

But... what if you're in a hungry little startup and really need to gather some UX metrics about user behavior, but can't find (or afford) an off-the-shelf package that does what you need.

And further... what if said product manager can write JavaScript that is so well-isolated that if it ever failed, it would fail silently and never negatively affect performance or the user in any way. (In fact, I can.)

Something like that could be injected into an application without developer involvement (using Google Tag Manager or the like). Marketers use those tools to stick all kinds of stuff onto websites and apps all the time. Why? Because they can be incredibly useful -- in fact, things like analytics tools are simply nonoptional nowadays -- and product engineers don't have to be bothered with the care and feeding of JavaScript snippets. They can instead go about creating new value.

By now, it should sound pretty reasonable that in certain cases, it's not a grave sin for well-isolated JavaScript that does some good job to get injected via a tag manager into a production web app, even if it was written by a lowly product manager.

> (Said product manager still needs to largely butt out of decisions that belong to the product engineers. We're talking about a bolt-on here.)

This was my story, and part of what my sturdy scripts do is gather metrics from our thousands of users in exactly the way we want them, inexpensively. 

I've distilled that down into `miserly-metrics`, and now, I'll finally explain it...

-----

## Documentation
`miserly-metrics` records DOM events and summarizes them. For instance, it will record all mouse travel, all clicks, all scrolling. It's not recording the individual events, just the amount of something. Moving the pointer 1000 pixels adds 1000 to the mousemove count.

For some user behaviors, it's important to also record the number of times something happened. For instance, if I'm got a nervous habit of wiggling the mouse as a read a web page, that will add up to a huge mousemove metric, but only one actual motion. Recording a "halt" (any pause in pointer travel) in addition to the total number of pixels moved lets us reason better when we're analyzing aggregate data on user behavior. 

When it's time to send the metrics to the server, it uses `xhr` to call an endpoint you define. In my case, it's a Lambda that then talks to an RDS instance of MySQL. Easy peasy (as long as you've got CORS enabled.)

You can trigger the `send()` method whenever, so this script works fine in a SPA (Single Page Application). I always recommend using the browser's `onunload` event to make sure it gets sent even if the browser is closed -- or, you might be fine with some of those metrics getting thrown away. It's an edge case, after all.

### The outcome
The outcome of all this is a SQL table that will let you query for the pages in your app that require unnecessarily high mouse travel, or where users are spending too much (or too little) time scrolling, etc. If your goal is to improve UX by reducing unnecessary mouse travel, well now you've got an easy way to track your progress.

These are the metrics that worked for us, but with a little bit of JavaScript and DOM knowledge, you can gather all kinds of more specific metrics, facts about the user or browser, etc.

### Structure

* `client/`
  * `miserly-metrics.js` -- this is the JavaScript client that gathers the metrics and submits them to the server
  * `mmtest.html` -- a trivial HTML implementation you can use to test the JavaScript (even works just by double-clicking top open it in a browser)
* `server/`
  * `lambda_function.py` -- the AWS Lambda that receives data from the client (through the AWS API Gateway, which must be CORS-enabled)
  * `mysql_ddl.sql` -- SQL script to create the very simple one-table database that collects metrics

### Dependencies and Usage

Any API can be set up to receive and handle the metrics package from my client. But, if you use the Lambda here, just be aware it has a couple of dependencies you'll need to include -- as described in the `.py` file.

Similarly, any database can be set up to store these simple metrics. (Well, I originally tried with Dynamo and it was a big PITA to do the kinds of queries I needed to do. Live and learn.) You can use MySQL as I did, or if you prefer Postgres or something, the DDL I've provided will get you started.

