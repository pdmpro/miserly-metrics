/*
Miserly Metrics - a tool to cheaply record key UX metrics (in summary form), like mousemoves,
mouse pauses ("halts"), clicks, etc.

See: https://github.com/pdmpro/miserly-metrics

TODO for Glen: add back durationSeconds?
*/
miserlyMetrics = (function() {
    // private members
    function log(msg, severity = "info") {
        // sugary function for logging specifically from this object
        console[severity](`miserlyMetrics: ${msg}`);
    }
    var domEventsInitialized = false;
    var uxMetrics = null;
    var apiEndpoint = null;
    var interestingDOMEvents = {
        // each entry here is a DOM event we're going to track
        // poll interval is used in state-end checking and may be omitted
        mousemove: {pollInterval: 123},
        scroll: {pollInterval: 234},
        resize: {pollInterval: 345},
        mouseleave: {pollInterval: null},
        click: {},
    }
    function initUXMetrics() {
        log("initializing miserly metrics");
        // start by setting up the shell for the collected event data
        uxMetrics = { summaries: {} }

        // sets up tracking for generic DOM events we're curious about
        for (let eventKind in interestingDOMEvents) {
            log(`setting up ${eventKind}`);
            // create an object that encapsulates properties and methods for each type of interesting event
            uxMetrics.summaries[eventKind] = {
                fireCount: 0,
                stateChangeTimeout: null,
                stateChangeCount: 0,
                handle(event) {
                    let trackingRecord;
                    try {
                        trackingRecord = uxMetrics.summaries[event.type];
                    } catch (e) {
                        // pass
                    }

                    if (trackingRecord) {
                        // count every time this fires (even for continuous-fire events)
                        trackingRecord.fireCount++;

                        // trick to track event state changes like when mouse travel ends, using
                        // timeouts and bound functions
                        let delay = interestingDOMEvents[event.type]["pollInterval"];
                        if (delay) {
                            if (trackingRecord.stateChangeTimeout) {
                                clearTimeout(trackingRecord.stateChangeTimeout);
                            }
                            trackingRecord.stateChangeTimeout = setTimeout(trackingRecord.handleStateEnd.bind(event), delay);
                        }
                    }
                }
                ,
                handleStateEnd() {
                    // thanks to how I'm using bind, "this" is the event
                    let trackingRecord = uxMetrics.summaries[this.type];
                    // keep track of the number of state changes
                    trackingRecord.stateChangeCount++;
                }
            }
            // set up the DOM listener for this metric
            if (!domEventsInitialized) {
                let target = (eventKind == "mouseleave") ? document.body : window;
                target.addEventListener(eventKind, uxMetrics.summaries[eventKind].handle);
            }
        }
        domEventsInitialized = true;
    }
    function sendUsageData() {
        // sends to a server if we know the URL, else returns false
        if (apiEndpoint) {
            let data = JSON.stringify({
                host: location.host, // useful to let you distinguish between a staging server vs. production in the database
                page: location.pathname,
                uxMetrics: uxMetrics
            });
            var xhr = new XMLHttpRequest();
            xhr.addEventListener("load", function() {
                console.info("event metric save complete:\n" + this.responseText);
                // I've decided to reset after every save; depending on your use case you might not want to,
                // or might not want to do it here. In any case, you should be checking for HTTP errors, unlike me.
                miserlyMetrics.init();
            });
            log(`sending to ${apiEndpoint}: \n${data}`);
            xhr.open("POST", apiEndpoint, true);
            xhr.setRequestHeader("Content-type", "application/json");
            xhr.send(data);
            return true;
        } else {
            console.error("miserlyMetrics can't send usage data without an API endpoint. call setEndpoint to set the URL");
            return false;
        }
    }

    return {
        // public members
        init() {
            initUXMetrics();
            this.dump();
        }
        ,
        dump() {
            if (uxMetrics) {
                log("metrics dump:");
                console.dir(uxMetrics);
            } else {
                log("metrics have not been initialized", "warn");
            }
        }
        ,
        send() {
            sendUsageData();
        }
        ,
        setEndpoint(url) {
            apiEndpoint = url;
        }
    }
})();
