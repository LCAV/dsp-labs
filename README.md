# DSP labs

## Viewing material from GitHub

Go [here](docs/README.md). Note that plug-in material won't render properly, e.g. equations.

## Building/viewing gitbook locally

You'll need [npm](https://www.npmjs.com/get-npm).

Install the `gitbook` client if you haven't already:
```bash
$ npm install gitbook-cli -g
```

Copy the repository and run the following commands from the top directory:
```bash
$ gitbook install
$ gitbook serve
```

Go to: `http://localhost:4000`


## GitBook instructions (from scratch)

[Installation instructions](https://toolchain.gitbook.com/setup.html).

```bash
$ npm install gitbook-cli -g
```

Create new directory
```bash
$ mkdir my-book
$ cd my-book
$ gitbook init
```

To preview the book and make live edits:
```bash
$ gitbook serve
```

To build static website:
```bash
$ gitbook build
```

To have separate documentation and code, create a `book.json` file with the following content:
```json
{
    "root": "./docs"
}
```
and place all files inside a folder called `'docs'`.


### Adding math

Add the following line to your `book.json` file:
```json
{
    "plugins": ["mathjax"]
}
```

If you are exporting to PDF, you will find a bug when using this version of `mathjax` (as of 11 Dec 2018).
[This fix](https://github.com/GitbookIO/gitbook/issues/1875) consists of using a forked version of `mathjax`, namely:
```json
{
    "plugins": ["mathjax@https://github.com/OrgVue/gitbook-plugin-mathjax.git#speech-fix"]
}
```
and installing the following package:
```bash
$ npm install svgexport -g
```

Install the plugin from within your gitbook directory
```bash
$ gitbook install
```

[More info](https://github.com/GitbookIO/plugin-mathjax).

### Converting LaTeX to Markdown

[Pandoc](https://pandoc.org/) is a great tool for this. For small sections, the [online tool](https://pandoc.org/try/) is generally sufficient.


### Adding drop-down menu for sidebar

Add the following plug-in to your `book.json` file:
```json
{
    "plugins": ["expandable-chapters"]
}
```

Install the plug-in by running:
```bash
$ gitbook install
```

[More info](https://www.npmjs.com/package/gitbook-plugin-expandable-chapters).

### Highlighted boxes (for tasks)

See [here](https://github.com/GitbookIO/plugin-hints).

### Adding Disqus commands

You'll need to make a Disqus account if you don't already have one.

Edit the `book.json` file as described [here](https://plugins.gitbook.com/plugin/disqus).

Install the plug-in by running:
```bash
$ gitbook install
```

### Adding custom favicon

See [here](https://www.npmjs.com/package/gitbook-plugin-custom-favicon).

### Adding TOC to page

See [here](https://www.npmjs.com/package/gitbook-plugin-simple-page-toc).


