# Changes in EU or Euro membership

In this rare case, edit and execute

    .scripts\eu-and-euro-countries.py

# Pickl files and Python scripts

pickl input files:
    .\scripts\council\barometer.pkl
    .\scripts\council\council-by-6weeks.pkl
    .\scripts\council\ecb-council-data.pkl


Each pickl file has a script, creating data for the website 
    .\scripts\prepare-council-barometer.py
    .\scripts\prepare-council-by-6weeks.py
    .\scripts\prepare-council-by-geography.py



# Adding new council members

* (assuming one-time setup of Python and modules + git clone of repo)

* Open a `Terminal` - a `command window`
    * Windows Explorer
    * Parent directory of    `ecb-monitor`
    * Right-click and choose `Open in Terminal`


* Do `git pull` before starting work

* Make changes to  
    `scripts\council\ecb-council-data.pkl`

* Process the changes
    `python .\scripts\prepare-council-by-geography.py`


* last line should be  ` output-3 [number over 100] rows`

* previous last line should end with `...\council-by-geography.js`


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

