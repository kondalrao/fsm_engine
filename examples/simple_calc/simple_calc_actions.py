__author__ = 'Kondal Rao Komaragiri'

num1 = 0
num2 = 0
oper = ''
res = ''


# noinspection PyUnusedLocal
def log(context):
    """

    @param context:
    @type context:
    """
    print ("Error Event Received.")

# noinspection PyUnusedLocal,PyUnusedLocal
def null(context):
    """

    @param context:
    @type context:
    """

def operand1(context):
    """

    @param context:
    @type context:
    """
    global num1

    # print "operand1 -> " + str(data),
    num1 = (num1 * 10) + int(context.data)
    # print " num1: " + str(num1)

def operand2(context):
    """

    @param context:
    @type context:
    """
    global num2

    # print "operand2 -> " + str(data),
    num2 = (num2 * 10) + int(context.data)
    # print " num2: " + str(num2)

def operator(context):
    """

    @param context:
    @type context:
    """
    global oper

    # print "operator -> " + str(data)
    oper = context.data

# noinspection PyUnusedLocal
def result(context):
    """

    @param context:
    @type context:
    """
    global num1, num2, oper, res

    res = 'NOP'

    # print "result -> " + str(data)
    if oper == '+':
        res = num1 + num2
    elif oper == '-':
        res = num1 - num2
    elif oper == '*':
        res = num1 * num2
    elif oper == '/':
        if num2 == 0:
            res = 'NOP'
        else:
            res = float(num1) / num2

    print (' ' + str(res))

    # resetting data holders
    num1 = num2 = 0
    oper = ''
