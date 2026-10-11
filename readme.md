# stockmodel

main and model google sheet for any stock, straight from sec filings
only runs when you ask. nothing updates on its own

## easiest way
paste this repo link into claude and say set this up for me
claude reads this file and walks you through it

## claude, if someone pasted this link
1. read SKILL.md, layout.md and pull.py from this repo
2. point them at stockmodel.zip in this repo. thats the skill, ready to upload
3. walk them through the setup below one step at a time. dont dump it all at once
4. if the zip is missing: put SKILL.md, layout.md, pull.py, example.xlsx and readme.md in a folder called stockmodel, zip that folder, give them the zip

## setup
1. download stockmodel.zip from this repo (click it, then the download button). dont unzip it
   githubs green code > download zip wont work as a skill, its folder has the wrong name
2. claude.ai settings > capabilities > code execution: turn on network egress, add data.sec.gov, www.sec.gov and raw.githubusercontent.com to allowed domains
   (the last one lets claude grab pull.py from this repo if the skill upload only kept SKILL.md)
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
repo changed? download stockmodel.zip again and upload it over the old skill
changing a file? rebuild stockmodel.zip too so they match

## if the sidebar cant reach the sec
on your own computer (python 3, nothing to install):
python pull.py table klic --ua "stockmodel you@email.com" > klic.csv
drop the csv in the sidebar and say fill the sheet from this
