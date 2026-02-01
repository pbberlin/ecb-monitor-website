# Adding blog articles

* Blog articles are written as single files in  
    `content/blog/de/`     
    `content/blog/en/`

* For editing use [VS Code](https://code.visualstudio.com/download)

* `[year-month-day].md` files - written in [Markdown format](https://en.wikipedia.org/wiki/Markdown#Examples)


## Run the Website on your notebook, so check results

* (assuming one-time setup of Python and modules)

* Open a `Termina` - a `command window`
    * Windows Explorer
    * Parent directory of    `ecb-monitor`
    * Right-click and choose `Open in Terminal`


* Do `git pull` before starting work

* Writing a blog post in English and German 
    * Files go in `/content/blog/en` and -`de`

* Title, subtitle, vignette
    * First  line is the blog title - appears in list and in detail view
    * Second line is the subtitle - appears only in list view
    * Third line is an optional vignette.
        * Available vignettes here `/templates/blog`
        * For instance `fhe-grey` 

* Links and content images
    * Write hyperlinks like this:  [link title](https://example.com)
    * Content image need to be saved under `/static/img/blog-[2026-mm-dd]`
    * Content image can then be references like this `![my image label](../../static/img/blog/my-image.jpg)`
    * Content image must be resized by hand

* Possible sources for content images 
    * [Adobe Stock Picture Database](https://stock.adobe.com/de/)
    * [wikimedia commons](https://commons.wikimedia.org/wiki/Main_Page)
    * Self-created images - by using Google Gemini nanon banana LLM.


* (todo) Edit `copyright.md`
    * Insert small version of the image
    * Add license info


* Run `cls && python app.py` to check your new content 
    * `F5` or `CTRL+R` to reload 

```sh
git add *
git commit -a -m "[my short description]"
git push
```

* Check your changes on [ecb-monitor.zew.de](https://ecb-monitor.zew.de)

---

## Images

https://stock.adobe.com/de


•	Geldpolitik 
    o	Expansiv versus restriktiv
    o	„Falke“ versus „Taube“
•	Zentralbank
•	Eurozone
•	Euro-Währung
•	EZB-Rat
•	EZB-Hauptsitz
•	Staatsanleihen
•	Anleihezinsen
•	Wirtschaftswachstum
•	Inflation
