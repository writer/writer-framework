---
layout: home
---

<div class="homeMain">
  <div class="topContainer_L1">
    <div class="topContainer_L2">
      <div class="taglines">
      <div class="primaryTagline">No-code in the front, Python in the back.</div>
      <div class="secondaryTagline">An open-source framework for creating data apps.</div>
      </div>
      <iframe width="840" height="472.5" src="https://www.youtube.com/embed/XBAPBy_zf8s" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
      <!-- <video src="./images/home.streamsync1min.mp4" controls autoplay loop></video> -->
      <div class="quickstart vp-doc">

```sh
# Install via pip (requires Python >= 3.9.2)
pip install "streamsync[ds]"

# Run local server for the demo app
streamsync hello
```

</div>
      <div class="topActions">
        <div class="actions">
          <a class="buttonLink" href="getting-started.html">
              <img src="./images/home.icon-arrow.svg" />
              Get started
          </a>
          <a class="buttonLink"  href="https://github.com/streamsync-cloud/streamsync" target="_blank" noreferrer noopener>
              <img src="./images/home.icon-github.svg" />
              View on GitHub
          </a>
        </div>
      </div>
    </div>
  </div>
  <div class="highlights">

<div class="box">
<div class="heading">
<h1>Reactive and state driven</h1>
</div>
<div class="inner vp-doc">

Streamsync is **fully state-driven** and provides **separation of concerns** between user interface and business logic. 

```py
import streamsync as ss

def handle_increment(state):
    state["counter"] += 1

ss.init_state({
    "counter": 0
})
```

The user interface is a template, which is defined visually. The template contains reactive references to state, e.g. `@{counter}`, and references to event handlers, e.g. when _Button_ is clicked, trigger `handle_increment`.

</div>
</div>


<div class="box">
<div class="heading">
<h1>Fast</h1>
</div>
<div class="inner vp-doc">

<img src="./images/home.fast.gif" />

- Event handling adds **minimal overhead** to your Python code (~1-2ms).
- The script only runs once.
- **Non-blocking by default**. Events are handled asynchronously in a thread pool running in a dedicated process.

</div>
</div>


<div class="box">
<div class="heading">
<h1>Developer-friendly</h1>
</div>
<div class="inner vp-doc">

- **Version control everything**. Development is local, user interfaces are saved as JSON.
- **Use your local code editor and get instant refreshes** when you save your code. Alternatively, use the provided web-based editor.
- You edit the UI while your app is running. **What you see really is what you get**.

</div>
</div>


<div class="box">
<div class="heading">
<h1>Flexible</h1>
</div>
<div class="inner vp-doc">

- Elements are highly customisable with **no CSS required**, allowing for shadows, button icons, background colours, etc.
- **HTML elements with custom CSS may be included** using the _HTML Element_ component. They can serve as containers for built-in components.

</div>
</div>
  </div>

  <div class="bottomActions">
    <h1>Ready to dive in?</h1>
    <div class="actions">
      <a class="buttonLink" href="getting-started.html">
          <img src="./images/home.icon-arrow.svg" />
          Get started
      </a>
      <a class="buttonLink"  href="https://github.com/streamsync-cloud/streamsync" target="_blank" noreferrer noopener>
          <img src="./images/home.icon-github.svg" />
          View on GitHub
      </a>
    </div>
  </div>

</div>

<style>

.homeMain h1 {
  font-size: 1.8rem;
}

.homeMain .topContainer_L1 {
  background: rgb(41,207,0);
  background: linear-gradient(180deg, rgba(41,207,0,1) 1%, rgba(145,231,78,1) 50%, rgba(145,231,78,1) 95%, #ffffff 100%);
}

.homeMain .topContainer_L2 {
  background: url(images/home.wave.svg) no-repeat bottom left;
  background-size: contain;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

html.dark .homeMain .topContainer_L2 {
  background: url(images/home.darkwave.svg) no-repeat bottom left;
  background-size: contain;
}

.homeMain .taglines {
  text-align: center;
  line-height: 1.3;
  color: white;
  margin: 72px 48px 48px 48px;
}

.homeMain .primaryTagline {
  font-weight: bold;
  font-size: 2.5rem;
}

.homeMain .secondaryTagline {
  font-size: 1.5rem;
}

.homeMain video {
  width: min(800px, 90vw);
  box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.5);
  border-radius: 8px;
}

.homeMain .actions {
  color: white;
  display: flex;
  gap: 16px;
  margin-left: 16px;
  margin-right: 16px;
  align-items: center;
  justify-content: center;
}

.homeMain .quickstart {
  width: min(720px, 100vw);
  padding: 24px;
  border-radius: 8px;
  margin-left: auto;
  margin-right: auto;
  margin-top: 24px;
  overflow: hidden;
}

.homeMain .topActions {
  margin-top: 24px;
  margin-bottom: 72px;
  width: 100%;
}

.homeMain a.buttonLink {
  background: linear-gradient(180deg, #606060 1%, #303030 100%);
  color: white;
  border-radius: 32px;
  padding: 8px 16px 8px 16px;
  box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.5);
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  flex: 0 1 180px;
  cursor: pointer;
  font-size: 0.9rem;
}

.homeMain a.buttonLink img {
  max-width: 16px;
}

.homeMain .highlights {
  padding: 16px;
  margin-left: auto;
  margin-right: auto;
  max-width: min(var(--vp-layout-max-width), 100ch);
  width: 100%;
}

.homeMain .highlights .box:not(:first-of-type) {
  margin-top: 48px;
}

.homeMain .highlights .box .heading {
  color: #29cf00;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.homeMain .highlights .box .heading img {
  max-height: 24px;
  max-width: 24px;
}

.homeMain .highlights .box h1 {
  background-image: linear-gradient(#29cf00, #91E74E);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  -webkit-text-fill-color: transparent; 
  -moz-text-fill-color: transparent;
  min-height: 32px;
  display: flex;
  align-items: center;
}

.homeMain .highlights .box .inner {
  background-color: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  padding: 16px;  
  border-radius: 8px;
  max-width: 100%;
  overflow: hidden;
  box-shadow: 0 0 24px -4px rgba(0, 0, 0, 0.2);
}

.dark .homeMain .highlights .box .inner {
  background-color: black;
}

.homeMain .highlights .box .inner img {
  margin-left: auto;
  margin-right: auto;
  max-width: min(400px, 100%);
}

.homeMain ul {
  list-style-type: circle;
  margin-left: 4px;
}

.homeMain .bottomActions {
  margin-top: 96px;
  width: 100%;
  text-align: center;
}

.homeMain .bottomActions h1 {
  margin-bottom: 24px;
}

</style>

