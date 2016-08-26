import httplib
import sys
import operator
from lxml import html


def getDataFromGoogleFinance(ticker):
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
                    if dataValue:
                        if 'key' in column.values():
                            dataKey = column.text.strip()
                        elif 'val' in column.values():
                            dataValue = column.text.strip()
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


def parseCsv(csvFile):
    tickerList = ['DIA', 'EZJ']
    return tickerList


def prettyDataPrint(dataList, sortBy='Ticker', reverse=False):
    print ""
    formatString = ""
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
    for attribute in attributes:
        getAttribute = operator.itemgetter(attribute)
        attributeMaxLen = len(attribute)
        for i in dataList:
            attributeMaxLen = max(len(getAttribute(i)), attributeMaxLen)
        formatString += "{:<%s} | " % str(attributeMaxLen + 2)
    textToPrint = formatString.format(*attributes)
    print "-" * len(textToPrint)
    print textToPrint
    print "-" * len(textToPrint)
    dataList.sort(key=operator.itemgetter(sortBy), reverse=reverse)
    for data in dataList:
        dataValue = []
        for attribute in attributes:
            dataValue.append(data[attribute])
        print formatString.format(*dataValue)


def printStatus(total, counter):
    percentage = 100 * counter / total
    sys.stdout.write("\rProgress: [%s] %d%%" % ("{:<20}".format("=" * (percentage/5)), percentage))
    sys.stdout.flush()


def sortByMapper(sortBy):
    if sortBy == "ticker":
        return "Ticker"
    elif sortBy == "open":
        return "Open"
    elif sortBy == "mktcap":
        return "Mkt cap"
    elif sortBy == "dividend":
        return "Dividend"
    elif sortBy == "yield":
        return "Div. yield"
    elif sortBy == "eps":
        return "EPS"
    elif sortBy == "shares":
        return "Shares"


def main(tickerList, sortBy='ticker', reverse=False):
    failedTickers = []
    dataList = []
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

    helpString = '''Usage:
./%s [options] tickers

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
