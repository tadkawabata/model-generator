# stockmodel

main and model google sheet for any stock, straight from sec filings
only runs when i ask

## setup
1. put your name and email in the ua line at the top of pull.py (sec wants it). keep the repo private if you dont want it public
2. upload these files to a github repo
3. claude.ai settings > capabilities > code execution: network egress on, add data.sec.gov and www.sec.gov to allowed domains
4. github > code > download zip, then claude > customize > skills > upload a skill. if it says the zip is invalid, put the files in a folder called stockmodel and zip that folder
5. install claude for google workspace from the google workspace marketplace
6. open example.xlsx in google sheets once to see whats what
7. new blank google sheet > extensions > claude > open claude > say run stockmodel check, then set up klic
8. after that just open the sheet and say run stockmodel. keep the sidebar open while it works
9. changed something? edit on github, download zip, upload the skill again

## files
SKILL.md  what claude does when i say run stockmodel
layout.md  tabs, rows, columns
pull.py  pulls the sec numbers. python pull.py check, latest <ticker>, table <ticker>
example.xlsx  example sheet, explanations where the numbers go

## if the sidebar cant reach the sec
run python pull.py table klic > klic.csv on my laptop (python 3, nothing to install), drop the csv in the sidebar
