# Adding blog articles to ecb-monitor.zew.de

## One time preparations

* (one-time setup of Python and modules + git clone of repo, usually done for you by pbu)

* Install [VS Code](https://code.visualstudio.com/download)

## Structure of the blog content

* Blog articles are written as single files in  
    `content/blog/policy/de/`     
    `content/blog/policy/en/`
    or
    `content/blog/science/de/`     
    `content/blog/science/en/`


* Files are named `[year-month-day].md`

* Files are Written in [Markdown format](https://en.wikipedia.org/wiki/Markdown#Examples)

* For editing use [VS Code](https://code.visualstudio.com/download)

* Create English and German versions in ...`/en` and in `/de`

## Run the Website on your notebook, to check results

* Windows Explorer

* Navigatate to parent directory of    `ecb-monitor`
    * Usually somewhere under "Documents" - "Meine Dokumente"

* Right-click on folder icon - and choose `Open in Terminal`

### In the `black` terminal window

* Be sure, that the `prompt` line ends with ...`ecb-monitor>`

* Enter `git pull`
    * Usually resonse is `Already up to date.`

* Keep the black window open


### Switch to Windows Explorer again

* Navigatate to directory  `ecb-monitor/content/blog/[policy|science]/en` and -`de`

* Now create new files with extension `.md` 
    * You can also copy an existing file and rename it

* Open the new files with VS Code

* Writing a blog post in English and German 

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

<!-- 
* (todo) Edit `copyright.md`
    * Insert small version of the image
    * Add license info
-->

## Check your new content

* To check your new content<br>in the website locally on your own notebook

* Switch to the `black` terminal window
    * Start the website on your notebook
    * Enter   `python app.py`
    * Response should end with `* Running on http://192.168.178.80:5000`

* Go to your web browser and open `http://localhost:5000/`
    * Navigate to the `ECB-Watching – der Kommentar`
    * Navigate to the `Neues aus der Forschung`
    * Check your new blog content


* Switch to VS Code - and change your blog conten (German and English)

* Switch back to your web browser
    * `F5` or `CTRL+R` to reload 
    * Check your changes


## Bring your changes live

* Make your changes visible on [ecb-monitor.zew.de](https://ecb-monitor.zew.de)

* Go to the black terminal window

* Enter these three lines  
```sh
    git add *
    git commit -a -m "[my short description]"
    git push
```

* The last line `git push` should result in a 20 lines response

* Check your changes on [ecb-monitor.zew.de](https://ecb-monitor.zew.de)




---



## Image sources

Possible images for your blog content

* https://commons.wikimedia.org/wiki/Main_Page

* https://stock.adobe.com/de
