# layout

template.xlsx is the source of truth for how a sheet looks: tab names, labels, widths, colors, number formats and formulas
every company sheet starts as a copy of the template. claude fills values and notes, the template owns the look
example.xlsx is the same layout with an explanation in every cell
this file says what goes where. the exact labels are in the template

## text in the sheet
1. proper case, the way a published model reads. sentences start with a capital
2. labels exactly as the template has them, eg Revenue, Gross margin, SG&A, EPS ($)
3. fiscal labels Q3 FY26, FY25, Proj. kinds Quarter, Derived quarter, Fiscal year, Proj
4. filings written the normal way: 10-K, 10-Q, 8-K
5. tickers in caps. company and product names styled the way the company writes them (BioCryst, ORLADEYO)
6. NM (not meaningful) when a ratio means nothing, never a junk number
7. pull.py already prints labels, sources and check results this way. copy them as they are

## readable without clicking
1. long text wraps inside its cell. it never spills into the next column
2. source cells are a short label linked to the filing, eg =HYPERLINK("https://www.sec.gov/Archives/edgar/data/882796/000162828026053300/","10-Q Q2 FY26")
   pull.py prints the label and the link. the accession number and xbrl tag go in that cells note
3. anything that changes how you read a number goes in a visible note cell, one short sentence
4. text rows show the summary itself. exact quotes stay in cell notes
5. cell notes only hold quotes, accession numbers and xbrl tags. nothing i need to read hides in a note

## units
everything in $ millions unless the label says otherwise, main tab included
a $4.25 trillion market cap is 4,254,000.0, never 4.25T. price is in $, shares in millions, eps in $

## main tab (columns a to e: label, value, as of, source, note)
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

## model tab
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

## log tab
run date, latest period, what changed, filings used (short linked labels), checks
one row per run, newest at the bottom

## new quarter
1. insert a column right after the newest quarter. the years and my proj columns slide right, nothing gets deleted
2. sheets copies the format from the column to its left. fill the new column, then copy the formula rows (gross margin, operating margin, tax rate, fcf) from its neighbor
3. rewrite revenue y/y in every quarter and proj column so it points 4 quarters back
4. new fiscal year from a 10-K: insert a column right after the newest fiscal year the same way
5. old quarters stay. history only grows
the main tab ttm formulas find the newest 4 quarters on their own
