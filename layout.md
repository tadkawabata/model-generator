# layout

real sheets only have labels and numbers. what each cell means lives in example.xlsx
keep these spots the same in every sheet so later tabs (dcf, comps) can point at them

## main tab
label in a, value in b, as of date or source in c

1 ticker
2 company
3 cik
4 fiscal year end
5 price  (plain number from the last run, date in c)
6 shares out  (millions, 10q or 10k cover page)
7 market cap  =IF(OR(B5="",B6=""),"",B5*B6)
8 cash and st investments
9 debt
10 ev  =IF(B7="","",B7-B8+B9)
11 ev / sales ttm  ev over the last 4 quarters of revenue on the model tab
12 p/e ttm  market cap over the last 4 quarters of net income on the model tab
13 backlog
14 business  (2 or 3 lines)
15 customers
16 end markets
17 products
18 competitors
19 notes (mine)

## model tab
labels in a, numbers start in b
freeze column a and rows 1 to 5

header rows
1 fiscal label  eg q3 fy26, fy25, proj
2 period end
3 weeks
4 kind  quarter, derived quarter, fiscal year, proj
5 source  10q or 10k accession number

columns, left to right
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

formulas, always the same column, always blank when an input is blank
gross margin  =IF(OR(B10="",B7=""),"",B10/B7)
operating margin  =IF(OR(B15="",B7=""),"",B15/B7)
tax rate  =IF(OR(B19="",B18="",B18=0),"",B19/B18)
fcf  =IF(OR(B25="",B26=""),"",B25-B26)
revenue y/y  points at the column 4 quarters back (or 1 fiscal year back). leave it empty when that column isnt in the sheet

formats
$ millions  #,##0.0;(#,##0.0)
eps  0.00;(0.00)
ratios  0.0%
shares  #,##0.0
approx cells get a cell note that says approx and why

## log tab
row 1 headers
a run date
b latest period
c what changed
d filings used
e checks passed or failed

## new quarter
insert a column right after the newest quarter. the years and my proj columns slide right, nothing gets deleted
new fiscal year from a 10k: insert a column right after the newest fiscal year the same way
old quarters stay. history only grows
