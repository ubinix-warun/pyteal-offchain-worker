
import websocket, socket
import json

import threading

def subscriber(addr, on_msg_globalstate):
    def sub_on_message(wsapp, message):
        # print(message)

        objMsg = json.loads(message)
        # print(objMsg["EvalDelta"]["GlobalDelta"])
        if objMsg["EvalDelta"]["GlobalDelta"] != None:
            on_msg_globalstate(objMsg["EvalDelta"]["GlobalDelta"])

    def sub_on_error(ws, error):
        print("Subscriber got error.")
        print(error)
        print("#####################")

    def sub_on_close(ws, close_status_code, close_msg):
        print("Subscriber's offline.")

    def sub_on_open(ws):
        print("Subscriber's connected to", addr,"\n")

    global wsapp

    wsapp = websocket.WebSocketApp(addr, 
                              on_open=sub_on_open,
                              on_message=sub_on_message,
                              on_error=sub_on_error,
                              on_close=sub_on_close)
    wsapp.run_forever(sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY,1),))


def subscriber_exit():
    wsapp.close()

def subscriber_run(addr,on_msg_globalstate):
    x = threading.Thread(target=subscriber, args=(addr,on_msg_globalstate,))
    x.start()

    return x