# Adding blog articles

* Blog articles are written as single files in  
    `content/blog/policy/de/`     
    `content/blog/policy/en/`
    or
    `content/blog/science/de/`     
    `content/blog/science/en/`


* For editing use [VS Code](https://code.visualstudio.com/download)

* `[year-month-day].md` files - written in [Markdown format](https://en.wikipedia.org/wiki/Markdown#Examples)

* Create matching files in ...`/en` and in `/de`


## Run the Website on your notebook, so check results

* (assuming one-time setup of Python and modules + git clone of repo)

* Open a `Terminal` - a `command window`
    * Windows Explorer
    * Parent directory of    `ecb-monitor`
    * Right-click and choose `Open in Terminal`


* Do `git pull` before starting work

* Writing a blog post in English and German 
    * Files go to  `/content/blog/[policy|science]/en` and -`de`

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


* To check your new content<br>locally on your own notebook
    * `cls && python app.py`
    * `F5` or `CTRL+R` to reload 


* Commit your changes and publish them  
    ```sh
    git add *
    git commit -a -m "[my short description]"
    git push
    ```

* Check your changes on [ecb-monitor.zew.de](https://ecb-monitor.zew.de)

---

## Image sources

* https://commons.wikimedia.org/wiki/Main_Page

* https://stock.adobe.com/de


Search for

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
