# Frontend scripts

Streamsync can import custom JavaScript/ES6 modules from the frontend. Module functions can be triggered from the backend.

## Importing an ES6 module

Similarly to [stylesheets](/stylesheets), frontend scripts are imported via Streamsync's `mail` capability. This allows you to trigger an import for all or specific sessions at any time during runtime. When the `import_frontend_module` method is called, this triggers a dynamic [import()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import) call in the frontend.

The `import_frontend_module` method takes the `module_key` and `specifier` arguments. The `module_key` is an identifier used to store the reference to the module, which will be used later to call the module's functions. The `specifier` is the path to the module, such as `/static/mymodule.js`. It needs to be available to the frontend, so storing in the `/static/` folder is recommended.

The following code imports a module during event handling.

```py
def handle_click(state):
    state.import_frontend_module("my_script", "/static/mymodule.js")
```

If you want the module to be imported during initialisation, use the initial state.

```py
initial_state = ss.init_state({
    "counter": 1
})

initial_state.import_frontend_module("my_script", "/static/mymodule.js")
```

::: tip Use versions to avoid caching
Similarly to stylesheets, your browser may cache modules, preventing updates from being reflected. Append a querystring to invalidate the cache, e.g. use `/static/script.js?3`. 
:::

## Writing a module

The module should be a standard ES6 module and export at least one function, enabling it to be triggered from the backend. As per JavaScript development best practices, modules should have no side effects.

An example of a module is shown below.

```js
let i = 0;

export function sendAlert(personName) {
    i++;
    alert(`${personName}, you've been alerted. This is alert ${i}.`);
}
```

## Calling a function

Once the module is imported, functions can be called from the backend using the `call_frontend_function` method of state. This function takes three arguments. The first, `module_key` is the identifier used to import the module. The second, `function_name` is the name of the exported frontend function. The third, `args` is a `List` containing the arguments for the call. 

The following event handler triggers the frontend function defined in the section above.

```py
def handle_click(state):
    state.call_frontend_function("mymodule", "sendAlert", ["Bob"])
```

## Import a JavaScript script

Streamsync can also import and run JavaScript scripts directly, for their side effects. These are imported via the report's `import_script` method. This method takes two arguments. The first, `script_key` is the identifier used to import the script. The second, `path` is the path to the file. The specified path must be available to the frontend, so storing it in your application's `./static` folder is recommended.

```py
initial_state = ss.init_state({
    "counter": 1
})

initial_state.import_script("my_script", "/static/script.js")
```

::: warning Prefer ES6 modules
Importing scripts is useful to import libraries that don't support ES6 modules. When possible, use ES6 modules. The `import_script` syntax is only used for side effects; you'll only be able to call functions from the backend using modules that have been previously imported via `import_frontend_module`.  
:::

## Importing a script or stylesheet from a URL

Streamsync can also import scripts and stylesheets from URLs. This is useful for importing libraries from CDNs. The `import_script` and `import_stylesheet` methods take a `url` argument, which is the URL to the script or stylesheet.

```python
initial_state = ss.init_state({
    "my_app": {
        "title": "My App"
    },
})

initial_state.import_script("lodash", "https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.js")
```

## Frontend core

You can access Streamsync's frontend core via `globalThis.core`, unlocking all sorts of functionality. Notably, you can use `getUserState()` to get values from state.

```js
export function alertHueRotationValue() {
    const state = globalThis.core.getUserState();
    console.log("State is", state);
}
```

::: warning Here be dragons
Effectively using Streamsync's core can be challenging and will likely entail reading its [source code](https://github.com/streamsync-cloud/streamsync/blob/master/ui/src/core/index.ts). Furthermore, it's considered an internal capability rather than a public API, so it may unexpectedly change between releases.
:::