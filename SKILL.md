---
name: stockmodel
description: builds and updates a shkreli style main and model google sheet for one stock from sec filings. use when i say run stockmodel, set up a ticker, or update the model
---

# stockmodel

one google sheet per company, copied from my stockmodel template. tabs: Main, Model, Log
the layout section at the bottom of this file says what goes in each cell. the template already has the labels, look and formulas
python moves the numbers, you read the text and quote it, checks run before anything counts

## where the numbers come from (pick one, dont troubleshoot)
1. i dropped a <TICKER>.csv in the chat: use it. thats pull.py table output. no sec requests, no email needed
2. no csv: first see if this sandbox is online at all. one python request to https://www.sec.gov/ with a 10 second timeout. any http answer (even 403) means online. no email needed for this
   online: pull.py sits next to this file (if its missing, download https://raw.githubusercontent.com/tadkawabata/models/main/pull.py once). ask for the contact email, run as below
   offline (cant resolve, timeout), or pull.py missing and the download fails: stop. no more network troubleshooting. dont ask for an email. tell me in one short message:
   "your sidebar cant reach the sec right now. on your computer, run this from your stockmodel folder and drop the file here:
   python3 pull.py table <TICKER> --ua "stockmodel you@email.com" > <TICKER>.csv
   or ask claude on your computer to make the stockmodel csv for <TICKER>"

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

## sec contact (only when you run pull.py yourself)
the sec wants a contact email on every request. nothing personal is saved in these files
1. use only an email i typed in this chat for this. never my account email, never one from memory or another chat. dont put any email in commands you suggest to me, write you@email.com
2. if i havent given one, ask and wait for my answer before any sec request
3. pass it on every pull.py command as --ua "stockmodel <email>"
4. never write it into the sheet, the log, a cell note or any file

## what a run does
1. read the ticker from Main b1. empty: ask me for it and write it in b1
2. python pull.py latest <ticker> --ua "stockmodel <email>"  gets the newest 10-Q or 10-K and its period end
3. compare with the last period in the Log tab
   nothing new: say nothing new since <period>, refresh the price snapshot, stop
   something new (or a fresh template): keep going
4. python pull.py table <ticker> --ua "stockmodel <email>" (or the csv i dropped), then write the numbers into the Model columns (layout below says where)
5. read the filing text only for what xbrl doesnt have. the csv has links to the filings. use the newest 10-K, the newest 10-Q and the newest earnings 8-K, older filings only to fill backlog or segments history
   segments, end markets, backlog, guidance, a 2 or 3 line business summary, customers, products, competitors
   every number you get this way gets a cell note with the exact quote and the filing link. anything that changes how to read it goes in the visible note column
   cant open the filings from here (no internet, no web fetch): leave those rows blank, list them in the log and tell me. never fill them from memory
6. price snapshot: put =GOOGLEFINANCE(ticker) in a scratch cell, read it, write the plain number into Main b5, todays date in c5, delete the scratch cell. if that fails ask me for the price
7. run the checks, write one row to the Log tab, mark anything that fails, never hide it
8. tell me in the sidebar what changed in plain words. no buy or sell calls, just what moved and what failed

if i say run stockmodel check, just run python pull.py check with the --ua and tell me the result
if i say run stockmodel format, fix only the text on this sheet so it matches the layout below: casing, short linked sources, caveats in the note column, text rows across b:e. no sec pull, no new numbers, no formatting changes. if something i typed is in the way, ask me

## reading pull.py table
it prints csv in 3 blocks with a blank line between them
1. Model: one column per period. header rows Fiscal label, Period end, Weeks, Kind, Source, Link, Accession, then the data rows with the template labels. Approx at the bottom lists estimated cells (derived Q4 shares and EPS). put an approx note on those
2. Main: label, value, as of, source, link, detail. source + link make the linked source cell. detail goes in that cells note (layout below)
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
6. only the rows in the layout below. nothing gets its own new row outside the segments and end markets blocks
7. if pull.py cant reach the sec, stop and walk me through the fix below. never guess numbers
8. no buy or sell calls
9. i should be able to read every tab without clicking into cells

## pull.py errors
1. it says the sec needs a contact email: --ua was missing. ask me for one and run it again
2. blocked, 403, cant resolve, timeout: thats the sidebar sandbox, not the setup. ask for the csv (see where the numbers come from). one try only

## things that bite
1. fiscal labels are the companys fiscal quarters, not calendar. trust the Fiscal label row from pull.py
2. Q4 has no 10-Q. its the fiscal year minus the 9 month ytd, so Kind says Derived quarter
3. 14 week quarters happen. Weeks shows it and checks flag it
4. a company that doesnt fit (a bank, no cogs or gross profit): pull.py stops. tell me the template doesnt fit, write nothing
5. no revenue at all (early biotech): fill what exists and say biotech mode isnt built yet
6. big one offs can sit inside revenue too (a license payment, a sale). other operating items wont catch those. if a quarters revenue jumps far off its run rate, read why and put it in a note
7. never hard code anything about one company

# layout

template.xlsx is the source of truth for how a sheet looks: tab names, labels, widths, colors, number formats and formulas
every company sheet starts as a copy of the template. claude fills values and notes, the template owns the look
example.xlsx is the same layout with an explanation in every cell
this section says what goes where. the exact labels are in the template

### text in the sheet
1. proper case, the way a published model reads. sentences start with a capital
2. labels exactly as the template has them, eg Revenue, Gross margin, SG&A, EPS ($)
3. fiscal labels Q3 FY26, FY25, Proj. kinds Quarter, Derived quarter, Fiscal year, Proj
4. filings written the normal way: 10-K, 10-Q, 8-K
5. tickers in caps. company and product names styled the way the company writes them (BioCryst, ORLADEYO)
6. NM (not meaningful) when a ratio means nothing, never a junk number
7. pull.py already prints labels, sources and check results this way. copy them as they are

### readable without clicking
1. long text wraps inside its cell. it never spills into the next column
2. source cells are a short label linked to the filing, eg =HYPERLINK("https://www.sec.gov/Archives/edgar/data/882796/000162828026053300/","10-Q Q2 FY26")
   pull.py prints the label and the link. the accession number and xbrl tag go in that cells note
3. anything that changes how you read a number goes in a visible note cell, one short sentence
4. text rows show the summary itself. exact quotes stay in cell notes
5. cell notes only hold quotes, accession numbers and xbrl tags. nothing i need to read hides in a note

### units
everything in $ millions unless the label says otherwise, main tab included
a $4.25 trillion market cap is 4,254,000.0, never 4.25T. price is in $, shares in millions, eps in $

### main tab (columns a to e: label, value, as of, source, note)
1 ticker  row 1 doubles as the header row
2 company  across b:c
3 cik
4 fiscal year end  m/d
5 price ($)  plain number from the last run. as of = run date, source GOOGLEFINANCE, note Snapshot, not live
6 shares out (m)  newest 10-Q or 10-K cover page
7 market cap ($m)  formula
8 cash and st investments ($m)  cash plus st investments. note shows the split
9 debt ($m)  note says whats in it and whats left out (leases, royalty financing, converts)
10 ev ($m)  formula
11 ev / sales (ttm)  formula, uses the newest 4 quarter columns on its own
12 p/e (ttm)  formula, same. note says why when its NM or distorted
13 backlog ($m)  blank if not reported, note says so
14 to 18 business, customers, end markets, products, competitors  text across b:e. cell note holds the short source, link and quotes
19 notes (mine)  mine, claude never touches it
merged rows dont grow on their own in google sheets. if text doesnt fit, make the row taller (about 21 pixels a line)

### model tab
columns: a labels, b to i quarters (8), j to l fiscal years (3), m to p proj (4)
header rows: 1 fiscal label, 2 period end, 3 weeks, 4 kind, 5 source (short linked label)
row 6 says $M unless noted
data rows
7 revenue
8 revenue y/y  formula
9 cogs
10 gross profit
11 gross margin  formula
12 sg&a
13 r&d
14 other operating items
15 operating income
16 operating margin  formula
17 interest and other
18 pretax income
19 taxes
20 tax rate  formula
21 net income
22 diluted shares (m)
23 eps ($)
25 cfo
26 capex
27 fcf  formula
29 backlog
30 guidance (next q revenue)  midpoint. low, high and the quote in the cell note
32 segments  label row, then up to 8 rows (33 to 40) for the reported segments. they add up to revenue
42 end markets  label row, then up to 8 rows (43 to 50) for the revenue breakdown the company leads with (product, end market or region). they add up to revenue
a company with more than 8: insert rows inside that block. one with fewer: leave the extra rows blank
nothing else gets its own row. any other breakdown goes in a cell note

formulas live in the template. claude never retypes them except revenue y/y after a new column (see below)
approx cells (derived q4 shares and eps) get a cell note that says approx and why

### log tab
run date, latest period, what changed, filings used (short linked labels), checks
one row per run, newest at the bottom

### new quarter
1. insert a column right after the newest quarter. the years and my proj columns slide right, nothing gets deleted
2. sheets copies the format from the column to its left. fill the new column, then copy the formula rows (gross margin, operating margin, tax rate, fcf) from its neighbor
3. rewrite revenue y/y in every quarter and proj column so it points 4 quarters back
4. new fiscal year from a 10-K: insert a column right after the newest fiscal year the same way
5. old quarters stay. history only grows
the main tab ttm formulas find the newest 4 quarters on their own
