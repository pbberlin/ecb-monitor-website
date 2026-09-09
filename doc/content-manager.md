# Adding blog articles to ecb-monitor.zew.de

## One time preparations

* (one-time setup of Python and modules + git clone of repo, usually done for you by pbu)

* Install [VS Code](https://code.visualstudio.com/download)

## Editorial content

* Articles in section 'News'

    * PDF files for quartely reports belong to 
        `static/pdf/quarterly-reports`

    * For page https://ecb-monitor.zew.de/md/quarterly-report.md  
      change Year and Quarter in   
        `content/md/en/quarterly-report.md`     
        `content/md/de/quarterly-report.md`     

    * https://ecb-monitor.zew.de/quarterly-reports-past   
        is generated automatically


    * https://ecb-monitor.zew.de/md/special-analyses.md
      change content in 
        `content/md/en/special-analyses.md`     
        `content/md/de/special-analyses.md`     


    ( 'News' _was_  a list of blog articles, taken from
        `content/blog/policy/de/`     
        `content/blog/policy/en/`
    )

* Section 'Science' blog - https://ecb-monitor.zew.de/blog/science 

    * Blog articles are written as single files in  
        `content/blog/science/en/`
        `content/blog/science/de/`     

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
```sh
remote:    github successful
To https://git.zew.de/ub-public-finance/ecb-monitor.git
   d106806..aa2ea37  main -> main
```

* Check your changes on [ecb-monitor.zew.de](https://ecb-monitor.zew.de)




---



## Image sources

Possible images for your blog content

* https://commons.wikimedia.org/wiki/Main_Page

* https://stock.adobe.com/de
