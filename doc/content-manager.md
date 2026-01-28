# Adding blog articles

* Blog articles are written as single files in  
    `content/blog/de/`     
    `content/blog/en/`

* [Markdown format](https://en.wikipedia.org/wiki/Markdown#Examples)


* Open a `Termina` - a `command window`
    * Windows Explorer
    * Parent directory of `ecb-monitor`
    * Right-click and choose `Open in Terminal`


* Do `git pull` before starting work

* Use VS Code for writing and editing a blog post in English and German 
    * Hyperlinks [link title](https://example.com)
    * Images need to be saved in `/static/img/blog-[2026-mm-dd]`
    * Images `![my image label](../../static/img/blog-2026-01-12/my-image.jpg)`
    * Images must be resized by hand

* Run `cls && python app.py` to check your new content 
    * `F5` or `CTRL+R` to reload 

```sh
git add *
git commit -a -m "[my short description]"
git push
```

* Check your changes on [ecb-monitor.zew.de](https://ecb-monitor.zew.de)
