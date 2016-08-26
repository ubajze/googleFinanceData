import httplib
import sys
import operator
from lxml import html


def getDataFromGoogleFinance(ticker):
    # Connect to the Google finance and get the basic info for specific ticker
    conn = httplib.HTTPSConnection("www.google.com")
    conn.request("GET", "/finance?q=%s" % ticker)
    response = conn.getresponse()
    if response.status == 200:
        responseData = response.read()
    else:
        responseData = None
    response.close()
    return responseData


def parseResponse(response):
    htmlData = html.fromstring(response)
    # Find element with class "snap-panel-and-plusone" which includes the table with the stock basic info
    divElement = htmlData.xpath('//div[@class="snap-panel-and-plusone"]')
    data = {}
    if len(divElement) == 1:
        subDivElement = divElement[0].xpath('//div[@class="snap-panel"]')
        for table in subDivElement[0].getchildren():
            for line in table.getchildren():
                dataKey = None
                dataValue = None
                lineElements = line.getchildren()
                for column in lineElements:
                    dataValue = column.text
                    # Store the info in each line of the table to the dictionary
                    # The google uses key and val elements in the HTML output
                    if dataValue:
                        if 'key' in column.values():
                            dataKey = column.text.strip()
                        elif 'val' in column.values():
                            dataValue = column.text.strip()
                # Separate dividend and dividend yield for better output
                if dataKey and dataValue:
                    if dataKey == 'Div/yield':
                        try:
                            data['Dividend'] = dataValue.split('/')[0]
                            data['Div. yield'] = dataValue.split('/')[1]
                        except IndexError:
                            data['Dividend'] = '-'
                            data['Div. yield'] = '-'
                    else:
                        data[dataKey] = dataValue
    return data

# Currently not supported
def parseCsv(csvFile):
    tickerList = []
    return tickerList


def sortByTicker(stockDict):
    return stockDict['Ticker']


def sortByOpen(stockDict):
    try:
        return float(stockDict['Open'])
    except:
        return stockDict['Open']


def sortByMktCap(stockDict):
    if 'M' in stockDict['Mkt cap']:
        return float(stockDict['Mkt cap'].replace('M', '')) * 1000000
    elif 'B' in stockDict['Mkt cap']:
        return float(stockDict['Mkt cap'].replace('B', '')) * 1000000000
    else:
        return float(stockDict['Mkt cap'])


def sortByPe(stockDict):
    try:
        return float(stockDict['P/E'])
    except:
        return stockDict['P/E']


def sortByDividend(stockDict):
    try:
        return float(stockDict['Dividend'])
    except:
        return stockDict['Dividend']


def sortByYield(stockDict):
    try:
        return float(stockDict['Div. yield'])
    except:
        return stockDict['Div. yield']


def sortByEps(stockDict):
    try:
        return float(stockDict['EPS'])
    except:
        return stockDict['EPS']


def sortByShares(stockDict):
    if 'M' in stockDict['Shares']:
        return float(stockDict['Shares'].replace('M', '')) * 1000000
    elif 'B' in stockDict['Shares']:
        return float(stockDict['Shares'].replace('B', '')) * 1000000000
    else:
        return float(stockDict['Shares'])


def prettyDataPrint(dataList, sortBy=None, reverse=False):
    print ""
    formatString = ""
    # The list of attributes that will be displayed
    attributes = ('Ticker',
                  'Range',
                  '52 week',
                  'Open',
                  'Vol / Avg.',
                  'Mkt cap',
                  'P/E',
                  'Dividend',
                  'Div. yield',
                  'EPS',
                  'Shares',
                  'Beta',
                  'Inst. own')
    # Find the max len for each columns to prepare the format for the output
    for attribute in attributes:
        getAttribute = operator.itemgetter(attribute)
        attributeMaxLen = len(attribute)
        for i in dataList:
            attributeMaxLen = max(len(getAttribute(i)), attributeMaxLen)
        formatString += "{:<%s} | " % str(attributeMaxLen + 2)
    # Print table header
    textToPrint = formatString.format(*attributes)
    print "-" * len(textToPrint)
    print textToPrint
    print "-" * len(textToPrint)

    if not sortBy:
        sortBy = sortByTicker

    # Sort the list of dictionary by specific key
    dataList.sort(key=sortBy, reverse=reverse)
    # Print the data in each disctionary to the output
    for data in dataList:
        dataValue = []
        for attribute in attributes:
            dataValue.append(data[attribute])
        print formatString.format(*dataValue)


def printStatus(total, counter):
    percentage = 100 * counter / total
    sys.stdout.write("\rProgress: [%s] %d%%" % ("{:<20}".format("=" * (percentage / 5)), percentage))
    sys.stdout.flush()


def sortByMapper(sortBy):
    # Map the sortBy to real keys
    if sortBy == "ticker":
        return sortByTicker
    elif sortBy == "open":
        return sortByOpen
    elif sortBy == "mktcap":
        return sortByMktCap
    elif sortBy == "pe":
        return sortByPe
    elif sortBy == "dividend":
        return sortByDividend
    elif sortBy == "yield":
        return sortByYield
    elif sortBy == "eps":
        return sortByEps
    elif sortBy == "shares":
        return sortByShares


def main(tickerList, sortBy='ticker', reverse=False):
    failedTickers = []
    dataList = []
    # Variables for printing the status bar
    numberOfTickers = len(tickerList)
    counter = 0
    printStatus(numberOfTickers, counter)
    for ticker in tickerList:
        data = parseResponse(getDataFromGoogleFinance(ticker))
        if data:
            data['Ticker'] = ticker
            # Exception for FRA exchange
            if data.get('Vol.'):
                data['Vol / Avg.'] = data.pop('Vol.')
            dataList.append(data)
        else:
            failedTickers.append(ticker)
        counter += 1
        printStatus(numberOfTickers, counter)
    sortBy = sortByMapper(sortBy)
    prettyDataPrint(dataList, sortBy, reverse)
    print ""
    for ticker in failedTickers:
        print "Unable to get data for ticker %s." % ticker


if __name__ == "__main__":

    tickerList = []
    sortBy = 'ticker'
    reverse = False

    fileName = sys.argv.pop(0)

    # The string that will be displayed when help is initiated
    helpString = '''Usage:
./%s [options] tickers

tickers\t\t\tThe list of tickers (Can be used with exchange - NASDAQ:GOOGL(recommended method))

Options:
-sort [option]\t\tSort table by (options: ticker, open, mktcap, pe, dividend, yield, eps, shares)
-rsort [option]\t\tSame as sort but descending
-csv [file]\t\tSpecify CSV export from Google Finance portfolio (you do not need to specify tickers in this case - in case you pass both options, tickers will be merged)
-help\t\t\tPrint this help
    ''' % (fileName)

    printHelp = False
    if "-sort" in sys.argv and "-rsort" in sys.argv:
        printHelp = True
    elif "-sort" in sys.argv or "-rsort" in sys.argv:
        try:
            if "-sort" in sys.argv:
                sortMethod = "-sort"
                reverse = False
            else:
                sortMethod = "-rsort"
                reverse = True
            sortOption = sys.argv[sys.argv.index(sortMethod) + 1]
            if sortOption in ['ticker', 'open', 'mktcap', 'pe', 'dividend', 'yield', 'eps', 'shares']:
                sortBy = sortOption
                sys.argv.pop(sys.argv.index(sortMethod))
                sys.argv.pop(sys.argv.index(sortOption))
            else:
                printHelp = True
        except:
            printHelp = True

    if "-help" in sys.argv:
        printHelp = True

    if "-csv" in sys.argv:
        try:
            csvFile = sys.argv[sys.argv.index("-csv") + 1]
            tickerList += parseCsv(csvFile)
            if not tickerList:
                print "Unable to parse CSV file."
                sys.exit(0)
            sys.argv.pop(sys.argv.index("-csv"))
            sys.argv.pop(sys.argv.index(csvFile))
        except:
            printHelp = True

    if len(sys.argv) == 0:
        printHelp = True

    if printHelp:
        print helpString
        sys.exit(0)

    tickerList += sys.argv

    main(tickerList, sortBy, reverse)
