---
name: stockmodel
description: builds and updates a shkreli style main and model google sheet for one stock from sec filings. use when i say run stockmodel, set up a ticker, or update the model
---

# stockmodel

one google sheet per company, copied from my stockmodel template. tabs: Main, Model, Log
layout.md says what goes in each cell. the template already has the labels, look and formulas
python moves the numbers, you read the text and quote it, checks run before anything counts
pull.py and layout.md sit next to this file. run pull.py from this folder
some installs only keep SKILL.md. if pull.py or layout.md is missing, download both before doing anything else:
https://raw.githubusercontent.com/tadkawabata/models/main/pull.py
https://raw.githubusercontent.com/tadkawabata/models/main/layout.md
if that download is blocked, tell me to add raw.githubusercontent.com to allowed domains, same place as the sec ones

## how you work on the sheet
1. edit the cells of the sheet that is open, directly. thats the only way you write
2. never build a file (xlsx, csv) and import it. never use file > import or replace spreadsheet. never upload anything to drive. never rename the file. never make new files or tabs
3. never change widths, fonts, colors, borders or number formats. the template owns the look. the only structural edits: insert a column for a new period, insert rows inside the segments or end markets block
4. never touch cells i typed: proj columns, notes (mine), anything you didnt write
5. if you cant write cells directly from where you are, stop and tell me. dont find a way around it
6. run from the claude sidebar inside the sheet (extensions > claude). if you are driving the sheet through a browser instead, stop and tell me to open the sidebar

## before anything: is this a template copy
look for tabs named Main, Model and Log with the template labels in column a
no: stop. tell me to open my stockmodel template, do file > make a copy, open the sidebar in the copy and ask again. dont build tabs yourself
an old sheet built before the template: same answer. a fresh copy plus set up <ticker> rebuilds it

## sec contact
the sec wants a contact email on every request. nothing personal is saved in these files
1. use only an email i typed in this chat for this. never my account email, never one from memory or another chat
2. if i havent given one, ask and wait for my answer before any sec request
3. pass it on every pull.py command as --ua "stockmodel <email>"
4. never write it into the sheet, the log, a cell note or any file

## what a run does
1. read the ticker from Main b1. empty: ask me for it and write it in b1
2. python pull.py latest <ticker> --ua "stockmodel <email>"  gets the newest 10-Q or 10-K and its period end
3. compare with the last period in the Log tab
   nothing new: say nothing new since <period>, refresh the price snapshot, stop
   something new (or a fresh template): keep going
4. python pull.py table <ticker> --ua "stockmodel <email>"  then write the numbers into the Model columns (layout.md says where)
5. read the filing text only for what xbrl doesnt have. use the newest 10-K, the newest 10-Q and the newest earnings 8-K, older filings only to fill backlog or segments history
   segments, end markets, backlog, guidance, a 2 or 3 line business summary, customers, products, competitors
   every number you get this way gets a cell note with the exact quote and the filing link. anything that changes how to read it goes in the visible note column
6. price snapshot: put =GOOGLEFINANCE(ticker) in a scratch cell, read it, write the plain number into Main b5, todays date in c5, delete the scratch cell. if that fails ask me for the price
7. run the checks, write one row to the Log tab, mark anything that fails, never hide it
8. tell me in the sidebar what changed in plain words. no buy or sell calls, just what moved and what failed

if i say run stockmodel check, just run python pull.py check with the --ua and tell me the result
if i say run stockmodel format, fix only the text on this sheet so it matches layout.md: casing, short linked sources, caveats in the note column, text rows across b:e. no sec pull, no new numbers, no formatting changes. if something i typed is in the way, ask me

## reading pull.py table
it prints csv in 3 blocks with a blank line between them
1. Model: one column per period. header rows Fiscal label, Period end, Weeks, Kind, Source, Link, Accession, then the data rows with the template labels. Approx at the bottom lists estimated cells (derived Q4 shares and EPS). put an approx note on those
2. Main: label, value, as of, source, link, detail. source + link make the linked source cell. detail goes in that cells note
3. Check, Result, Detail. results are OK, Flag or Fail. copy them into the Log as written

numbers are already $ millions to 1 decimal, EPS 2 decimals, shares millions. write them as they are
ratio rows in the csv are just for reading. in the sheet they are the template formulas
Main b8 is cash plus st investments added together, with the split in the note
Company comes out in title case. fix the styling from the 10-K cover (BioCryst, not Biocryst)

when a check says Missing or Newest filing Fail, that quarter isnt fully in the sec xbrl api yet or the company switched tags. read those numbers from the 10-Q itself, quote each one in a cell note, and say so in the log
when Main as of dates are older than the newest quarter, take cash, investments and debt from the newest 10-Q balance sheet with quotes
debt comes back blank (no debt tagged on the newest balance sheet): check the balance sheet. no borrowings means 0, and say so in the note
shares out comes back blank (multiple share classes): add up the classes from the 10-Q cover and quote it

## checks you do in the sheet (pull.py does 1 to 5, 7 and 9)
6. segment rows and end market rows each add up to revenue, within 0.5
8. no formula reads an empty cell
9. as of dates on Main match the latest period
10. every quoted number has its note, and the quote really is in that filing
put all of them in the Log row for the run. anything that fails: say so in the Log and in the sidebar

## hard rules
1. never type a financial number from memory. every number comes from pull.py or a quoted filing
2. edit the open sheet directly. never import, replace, upload or rename (how you work, above)
3. never touch cells i typed in
4. $ millions everywhere unless the label says otherwise. never 4.25T or 242.5B in a cell
5. proper case in the sheet, labels exactly as the template has them
6. only the rows in layout.md. nothing gets its own new row outside the segments and end markets blocks
7. if pull.py cant reach the sec, stop and walk me through the fix below. never guess numbers
8. no buy or sell calls
9. i should be able to read every tab without clicking into cells

## if the sidebar cant reach the sec
1. pull.py check says blocked or 403: claude.ai settings > capabilities > code execution, turn on network egress, add data.sec.gov and www.sec.gov to allowed domains
2. it says the sec needs a contact email: --ua was missing. ask me for one and run it again
3. still blocked: plan b, i run python pull.py table <ticker> --ua "stockmodel <email>" > <ticker>.csv on my laptop or in claude code, drop the csv into the sidebar, and you fill the sheet from it the same way

## things that bite
1. fiscal labels are the companys fiscal quarters, not calendar. trust the Fiscal label row from pull.py
2. Q4 has no 10-Q. its the fiscal year minus the 9 month ytd, so Kind says Derived quarter
3. 14 week quarters happen. Weeks shows it and checks flag it
4. a company that doesnt fit (a bank, no cogs or gross profit): pull.py stops. tell me the template doesnt fit, write nothing
5. no revenue at all (early biotech): fill what exists and say biotech mode isnt built yet
6. big one offs can sit inside revenue too (a license payment, a sale). other operating items wont catch those. if a quarters revenue jumps far off its run rate, read why and put it in a note
7. never hard code anything about one company
