# stockmodel

main and model google sheet for any stock, straight from sec filings
only runs when you ask. nothing updates on its own

## easiest way
paste this repo link into claude and say set this up for me
claude reads this file and walks you through it

## claude, if someone pasted this link
1. read SKILL.md, layout.md and pull.py from this repo
2. point them at stockmodel.zip and template.xlsx in this repo
3. walk them through the setup below one step at a time. dont dump it all at once
4. if the zip is missing: put SKILL.md, layout.md, pull.py, template.xlsx, example.xlsx and readme.md in a folder called stockmodel, zip that folder, give them the zip

## setup (once)
1. download stockmodel.zip from this repo (click it, then the download button). dont unzip it
   githubs green code > download zip wont work as a skill, its folder has the wrong name
2. claude.ai settings > capabilities > code execution: turn on network egress, add data.sec.gov, www.sec.gov and raw.githubusercontent.com to allowed domains
   (the last one lets claude grab pull.py from this repo if the skill upload only kept SKILL.md)
3. claude > customize > skills > upload a skill, pick the zip
4. install claude for google workspace from the google workspace marketplace
5. download template.xlsx, upload it to google drive, open it with google sheets, file > save as google sheets. name it stockmodel template. never type in it
6. open example.xlsx in google sheets once to see whats what

## each new company
1. open stockmodel template > file > make a copy. name it after the company
2. in the copy: extensions > claude > open claude
3. say run stockmodel check the first time, then set up <ticker>
4. give it a contact email when it asks (see your email below)
5. later just open that sheet and say run stockmodel. keep the sidebar open while it works

always run it from the sidebar inside the sheet. it edits cells directly and never imports or replaces anything
sheet text a bit off? say run stockmodel format. it only fixes text, no new numbers

## your email
the sec wants a contact email on every request, so claude asks for one at the start of a run
it only goes to the sec. its never saved in the sheet or in these files, so the repo has nothing personal in it

## files
SKILL.md  what claude does when you say run stockmodel
layout.md  what goes in each cell
pull.py  pulls the sec numbers. python pull.py check, latest <ticker>, table <ticker>, each with --ua "stockmodel you@email.com"
template.xlsx  the blank formatted sheet every company starts from
example.xlsx  the same sheet with an explanation in every cell

## updates
repo changed? download stockmodel.zip again and upload it over the old skill
changing a file? rebuild stockmodel.zip too so they match
template changed? old sheets keep the old look. make a new copy and set it up again if you want the new one

## if the sidebar cant reach the sec
on your own computer (python 3, nothing to install):
python pull.py table klic --ua "stockmodel you@email.com" > klic.csv
drop the csv in the sidebar and say fill the sheet from this
