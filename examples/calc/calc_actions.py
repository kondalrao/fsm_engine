
num1 = 0
num2 = 0
oper = ''
result = ''


def log(context, data):
    print "Logged"


def operand1(context, data):
    global num1

    print "operand1 -> " + str(data),
    num1 = (num1 * 10) + int(data)
    print " num1: " + str(num1)


def operand2(context, data):
    global num2

    print "operand2 -> " + str(data),
    num2 = (num2 * 10) + int(data)
    print " num2: " + str(num2)


def operator(context, data):
    global oper

    print "operator -> " + str(data)
    oper = data


def result(context, data):
    global num1, num2, oper

    print "result -> " + str(data)
    if oper == '+':
        result = num1 + num2
    elif oper == '-':
        result = num1 - num2
    elif oper == '*':
        result = num1 * num2
    elif oper == '/':
        if(num2 == 0):
            result = 'NOP'
        else:
            result = num1 / num2

    print result

    # resetting data holders
    num1 = num2 = 0
    oper = ''
