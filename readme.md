# stockmodel

main and model google sheet for any stock, straight from sec filings
only runs when you ask. nothing updates on its own

## easiest way
paste this repo link into claude and say set this up for me
claude reads this file and walks you through it

## claude, if someone pasted this link
1. read SKILL.md, layout.md and pull.py from this repo
2. put SKILL.md, layout.md, pull.py, example.xlsx and readme.md in a folder called stockmodel, zip that folder, give them the zip
3. walk them through the setup below one step at a time. dont dump it all at once
4. if you cant read the repo, ask them to download it (code > download zip) and drop the zip in the chat

## setup
1. get the skill zip from claude
   or by hand: git clone this repo and zip the folder. nothing to edit
2. claude.ai settings > capabilities > code execution: turn on network egress, add data.sec.gov and www.sec.gov to allowed domains
3. claude > customize > skills > upload a skill, pick the zip
4. install claude for google workspace from the google workspace marketplace
5. open example.xlsx in google sheets once to see whats what
6. new blank google sheet > extensions > claude > open claude > say run stockmodel check, then set up klic (or any ticker)
7. after that just open the sheet and say run stockmodel. keep the sidebar open while it works

## your email
the sec wants a contact email on every request, so claude asks for one at the start of a run
it only goes to the sec. its never saved in the sheet or in these files, so the repo has nothing personal in it

## files
SKILL.md  what claude does when you say run stockmodel
layout.md  tabs, rows, columns
pull.py  pulls the sec numbers. python pull.py check, latest <ticker>, table <ticker>, each with --ua "stockmodel you@email.com"
example.xlsx  example sheet, explanations where the numbers go

## updates
repo changed? paste the link into claude again and upload the new zip

## if the sidebar cant reach the sec
on your own computer (python 3, nothing to install):
python pull.py table klic --ua "stockmodel you@email.com" > klic.csv
drop the csv in the sidebar and say fill the sheet from this
