# layout

real sheets only have labels, numbers and short notes. what each cell means lives in example.xlsx
keep these spots the same in every sheet so later tabs (dcf, comps) can point at them

## readable without clicking
1. every column has a fixed width, wrap text on, align top. long text makes the row taller, it never spills into the next column
2. source cells are a short label linked to the filing
   eg =HYPERLINK("https://www.sec.gov/Archives/edgar/data/882796/000162828026053300/","10q q2 26")
   the link is the cik without leading zeros and the accession number without dashes
   the full accession number and xbrl tag go in that cells note
3. anything that changes how you read a number goes in a visible note cell, one short line
4. text rows show the summary itself. exact quotes stay in cell notes
5. a ratio that means nothing shows n/m (not meaningful), never a junk number
6. all text lowercase, company and product names too. the ticker in main b1 stays how i typed it
7. header rows bold with a light gray fill
8. numbers right aligned
   $ millions  #,##0.0;(#,##0.0)
   eps  0.00;(0.00)
   ratios  0.0%
   shares  #,##0.0
   multiples  0.0"x"
   dates  m/d/yy
9. cell notes only hold quotes, accession numbers and xbrl tags. nothing i need to read hides in a note

## main tab
columns
a label  width 22
b value  width 16
c as of  width 9
d source  width 13
e note  width 45, wraps

row 1 doubles as the header row: a ticker, b the ticker, c as of, d source, e note. bold, gray fill

rows
1 ticker
2 company  text across b:c merged
3 cik  source sec
4 fiscal year end  source sec
5 price  plain number from the last run. c the date, d googlefinance, e snapshot not live
6 shares out  millions, from the newest 10q or 10k cover page
7 market cap  =IF(OR(B5="",B6=""),"",B5*B6)
8 cash and st investments  added together. e shows the split, eg cash 155.0 + st inv 197.6
9 debt  e says whats in it and whats left out (leases, royalty financing, converts)
10 ev  =IF(B7="","",B7-B8+B9)
11 ev / sales ttm  ev over the last 4 quarters of revenue. n/m when that is 0 or less
12 p/e ttm  market cap over the last 4 quarters of net income. n/m when that is 0 or less, e says why
13 backlog  blank if they dont report it, e says so
14 business  2 or 3 lines, text across b:e merged
15 customers  across b:e merged
16 end markets  across b:e merged
17 products  across b:e merged
18 competitors  across b:e merged
19 notes (mine)  across b:e merged
rows 14 to 18 have no source cell. the cell note holds a short source with the link and the exact quotes
merged rows dont grow on their own in google sheets. set their row height to fit the text, about 21 pixels a line

## model tab
columns
a label  width 24
every period column  width 10
freeze column a and rows 1 to 5. wrap text on in rows 1 to 5

header rows
1 fiscal label  eg q3 fy26, fy25, proj
2 period end  m/d/yy
3 weeks
4 kind  quarter, derived quarter, fiscal year, proj
5 source  short linked label: 10q q3 26, 10k fy25
  derived q4 says 10k minus q3 and links the 10k. accession numbers in the cell note

column order, left to right
1. quarters oldest to newest (8 on the first build)
2. fiscal years oldest to newest (3 on the first build)
3. 4 projection quarters marked proj in row 1. mine, claude never touches them

data rows
7 revenue
8 revenue y/y  formula
9 cogs
10 gross profit
11 gross margin  formula
12 sga
13 r&d
14 other operating items
15 operating income
16 operating margin  formula
17 interest and other
18 pretax income
19 taxes
20 tax rate  formula
21 net income
22 diluted shares
23 eps
25 cfo
26 capex
27 fcf  formula
29 backlog
30 guidance  (next quarter revenue, low and high in the cell note)
32 segments  (header, then one row per segment under it)
after the segments, a blank row, then end markets (header, then one row per end market)
segments and end markets sit last because their row count changes by company

formulas, always the same column, blank when an input is blank, n/m when the math means nothing
gross margin  =IF(OR(B10="",B7=""),"",IF(B7<=0,"n/m",B10/B7))
operating margin  =IF(OR(B15="",B7=""),"",IF(B7<=0,"n/m",B15/B7))
tax rate  =IF(OR(B19="",B18=""),"",IF(B18<=0,"n/m",B19/B18))
fcf  =IF(OR(B25="",B26=""),"",B25-B26)
revenue y/y  points at the column 4 quarters back (or 1 fiscal year back). empty when that column isnt in the sheet, n/m when it is 0 or less
approx cells (derived q4 shares and eps) get a cell note that says approx and why

## log tab
widths: a 10, b 12, c 50, d 30, e 40. wrap text on, align top
row 1 headers, bold, gray fill
a run date
b latest period
c what changed
d filings used  short linked labels
e checks passed or failed

## new quarter
insert a column right after the newest quarter. the years and my proj columns slide right, nothing gets deleted
new fiscal year from a 10k: insert a column right after the newest fiscal year the same way
old quarters stay. history only grows
