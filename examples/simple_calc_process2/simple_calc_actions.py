__author__ = 'Kondal Rao Komaragiri'

import sys
sys.path.append('../..')

from fsm_engine import FSMContext

class calc_context(FSMContext):

    def __init__(self):
        FSMContext.__init__(self, None)
        self.num1 = 0
        self.num2 = 0
        self.oper = ''
        self.res = ''


# noinspection PyUnusedLocal
def log(context):
    print ("Error Event Received.")

# noinspection PyUnusedLocal
def null(context):
    pass

def operand1(context):

    #print "operand1 ", context.data

    # print "operand1 -> " + str(data),
    context.num1 = (context.num1 * 10) + int(context.data)
    # print " num1: " + str(num1)

def operand2(context):

    #print "operand2 ", context.data

    # print "operand2 -> " + str(data),
    context.num2 = (context.num2 * 10) + int(context.data)
    # print " num2: " + str(num2)

def operator(context):

    #print "operator ", context.data

    # print "operator -> " + str(data)
    context.oper = context.data

def result(context):
    context.res = 'NOP'

    print
    print "operand1 ", context.num1
    print "operator ", context.oper
    print "operand2 ", context.num2

    # print "result -> " + str(data)
    if context.oper == '+':
        context.res = context.num1 + context.num2
    elif context.oper == '-':
        context.res = context.num1 - context.num2
    elif context.oper == '*':
        context.res = context.num1 * context.num2
    elif context.oper == '/':
        if context.num2 == 0:
            context.res = 'NOP'
        else:
            context.res = float(context.num1) / context.num2

    print (' ' + str(context.res))

    # resetting data holders
    context.num1 = 0
    context.num2 = 0
    context.oper = ''

    if context.res is not 'NOP':
        context.num1 = context.res
