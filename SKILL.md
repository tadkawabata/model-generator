---
name: stockmodel
description: builds and updates a shkreli style main and model google sheet for one stock from sec filings. use when i say run stockmodel, set up a ticker, or update the model
---

# stockmodel

one google sheet per company. tabs: main, model, log. layout.md has every row and column
python moves the numbers, you read the text and quote it, checks run before anything counts
pull.py and layout.md sit next to this file. run pull.py from this folder
some installs only keep SKILL.md. if pull.py or layout.md is missing, download both before doing anything else:
https://raw.githubusercontent.com/tadkawabata/models/main/pull.py
https://raw.githubusercontent.com/tadkawabata/models/main/layout.md
if that download is blocked, tell me to add raw.githubusercontent.com to allowed domains, same place as the sec ones

## sec contact
the sec wants a contact email on every request. nothing personal is saved in these files
1. at the start of a run, ask me for a contact email if i havent given one in this chat. one question, then keep going
2. pass it on every pull.py command as --ua "stockmodel <email>"
3. never write it into the sheet, the log, a cell note or any file

## what a run does
1. read the ticker from main b1. blank sheet: ask me for the ticker and build the main, model and log tabs from layout.md
2. python pull.py latest <ticker> --ua "stockmodel <email>"  gets the newest 10q or 10k and its period end
3. compare with the last period in the log tab
   nothing new: say nothing new since <period>, refresh the price snapshot, stop
   something new: keep going
4. python pull.py table <ticker> --ua "stockmodel <email>"  then write the numbers into new or missing columns
5. read the filing text only for what xbrl doesnt have: segment and end market revenue, backlog, next quarter guidance from the 8k press release, a 2 or 3 line business description, customers, products, competitors. every number you get this way gets a cell note with the exact quote and the filing link
6. price snapshot: put =GOOGLEFINANCE(ticker) in a scratch cell, read it, write the plain number into main b5 with todays date in c5, delete the scratch cell. if that fails ask me for the price
7. run the checks, write results to the log tab, mark anything that fails, never hide it
8. tell me in the sidebar what changed in plain words. no buy or sell calls, just what moved and what failed

if i say run stockmodel check, just run python pull.py check with the --ua and tell me the result

## reading pull.py table
it prints csv in 3 blocks with a blank line between them
1. model: one column per period. header rows fiscal label, period end, weeks, kind, source, then the model rows in layout.md order. an approx row at the bottom lists cells that are estimates (derived q4 shares and eps). put an approx note on those cells
2. main: label, value, as of, source. shares out, cash, st investments, debt, each with its date and xbrl tag
3. checks: check, result, detail. results are ok, flag or fail

numbers are already $ millions to 1 decimal, eps 2 decimals, shares millions. write them as they are
ratio rows in the csv are just for reading. in the sheet they are formulas from layout.md
segments, end markets, backlog, guidance come out blank. thats step 5
main b8 is cash plus st investments added together

when a check says missing or newest filing fail, that quarter isnt fully in the sec xbrl api yet or the company switched tags. read those numbers from the 10q itself, quote each one in a cell note, and say so in the log
when main as of dates are older than the newest quarter, take cash, investments and debt from the newest 10q balance sheet with quotes
debt comes back blank (no debt tagged on the newest balance sheet): check the balance sheet. no borrowings means 0, and say so in the c cell

## checks you do in the sheet (pull.py does 1 to 5, 7 and 9)
6. segment rows and end market rows each sum to revenue, within 0.5
8. no formula reads an empty cell
9. as of dates on main match the latest period
10. every quoted number has its note, and the quote really is in that filing
put all of them in the log row for the run. anything that fails: color the cell light red and leave it

## hard rules
1. never type a financial number from memory. every number comes from pull.py or a quoted filing
2. never touch cells i typed in: projection columns, notes, anything i added
3. data rows are plain numbers. ratio rows are sheet formulas so i can click and see the math
4. $ millions to 1 decimal, eps to 2 decimals, shares in millions
5. if pull.py cant reach the sec, stop and walk me through the fix below. never guess numbers
6. no buy or sell calls

## if the sidebar cant reach the sec
1. pull.py check says blocked or 403: claude.ai settings > capabilities > code execution, turn on network egress, add data.sec.gov and www.sec.gov to allowed domains
2. it says the sec needs a contact email: --ua was missing. ask me for one and run it again
3. still blocked (the sidebar is new and might ignore that setting): plan b, i run python pull.py table <ticker> --ua "stockmodel <email>" > <ticker>.csv on my laptop or in claude code, drop the csv into the sidebar, and you fill the sheet from it the same way

## things that bite
1. fiscal labels are the companys fiscal quarters, not calendar. trust the fiscal label row from pull.py
2. q4 has no 10q. its the fiscal year minus the 9 month ytd, so kind says derived quarter
3. 14 week quarters happen. weeks row shows it and checks flag it
4. a company that doesnt fit (a bank, no cogs or gross profit): pull.py stops. tell me the template doesnt fit, write nothing
5. no revenue at all (early biotech): fill what exists and say biotech mode isnt built yet
6. never hard code anything about klic. it was just the test company
