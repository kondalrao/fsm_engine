fsm_engine
==========

The idea here to view each FSM as an independent container for processing events. These FSM containers can run in different threads/processes/nodes. Since the data and event are together, the event dispatch can send the pair to any FSM container. The trick here is to make sure that the FSM container doesn't maintiain any context of the data. So there is a centralized data/context repository which is used by the FSM containers and the event dispatch would just pick the context-event pair and send it to a free FSM container.

The order of state, event matching is done as following sequence.
  (state, event) -> (action, next_state)
  (state, any) -> (action, next_state)
  (any, event) -> (action, next_state)
  (any, any) -> (action, next_state)

A lot of work and change of design is needed. Any help/suggestions are very helpful.

TODO:
* Use other FSM containers other than XML like yaml/json.
* Enhance the event dispatch mechanism.


###Simply create an fsm in XML.
```
<?xml version="1.0"?>
<fsm name='calc'>
    <import>simple_calc_actions</import>
    <states prefix="">
        <init>DIGIT1</init>
        <state>DIGIT1</state>
        <state>DIGIT2</state>
    </states>
    <events prefix="">
        <event>DIGIT</event>
        <event>OPERATOR</event>
        <event>WS</event>
        <event>RESULT</event>
    </events>
    <actions prefix="">
        <action>operand1</action>
        <action>operand2</action>
        <action>operator</action>
        <action>result</action>
    </actions>
    <tables>
        <table state='DIGIT1' event='DIGIT' action='operand1' next_state='DIGIT1'/>
        <table state='DIGIT1' event='OPERATOR' action='operator' next_state='DIGIT2'/>
        <table state='DIGIT2' event='DIGIT' action='operand2' next_state='DIGIT2'/>
        <table state='DIGIT2' event='RESULT' action='result' next_state='DIGIT1'/>
        <table state='Any' event='WS' action='null' next_state='Same'/>
        <table state='Any' event='Any' action='log' next_state='Same'/>
    </tables>
</fsm>
```

###Define actions
```
num1 = 0
num2 = 0
oper = ''
res = ''

def log(context):
    print ("Error Event Received.")

def null(context):
    pass

def operand1(context):
    global num1
    
    num1 = (num1 * 10) + int(context.data)

def operand2(context):
    global num2

    num2 = (num2 * 10) + int(context.data)

def operator(context):
    global oper

    oper = context.data

def result(context):
    global num1, num2, oper, res

    res = 'NOP'

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
```

###Register and Fire events
```
import sys
sys.path.append('../..')

from fsm_engine import FSM

fsm_obj = None

def get_datatype(data):
    if data in ['+', '-', '*', '/']:
        return 'OPERATOR'
    elif data.isdigit():
        return 'DIGIT'
    elif data.isspace():
        return 'WS'
    elif data == '=' or data == '\n':
        return 'RESULT'

def initialize():
    global fsm_obj

    fsm_obj = FSM('calc.xml')

def main():
    initialize()

    fd = open('calc.txt')

    for line in fd.readlines():
        print (line.strip('\n'), end=''),

        for ch in line:
            if ch is not '\n':
                ev = get_datatype(ch)
                if ev is not 'WS' or ev is not 'RESULT':
                    fsm_obj.dispatch(event=ev, data=ch)
                else:
                    fsm_obj.dispatch(event=ev)

if __name__ == '__main__':
    main()
```

######Sample text file used (calc.txt)
```
1 + 2 =
123 + 321 =
10/2=
10/0=
```
