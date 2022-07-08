import sys
from time import time, sleep

from algosdk import account, encoding
from algosdk.logic import get_application_address
from offchain.operations import (
    createOffChainApp,
    waitOffChainAppReadyToRequest,
    requestDataFeed,
    ackDataFeed,
    updateDataFeed,
)

import requests
import json
from jsonpath_ng import jsonpath, parse

from offchain.subscriber import (
    subscriber,
    subscriber_run,
    subscriber_exit
)

from offchain.util import (
    getAppGlobalState,
)

from offchain.testing.setup import getAlgodClient
from offchain.testing.resources import (
    getTemporaryAccount,
)

def demo():
    client = getAlgodClient()

    print("Generating temporary accounts...")
    creator = getTemporaryAccount(client)

    print("offchain creator account: ", creator.getAddress())

    # Create Offchain contract.
    appID = createOffChainApp(
        client=client,
        operator=creator
    )
    print(
        "Done. The OffChain app ID is",
        appID,
        "\nand the offchain account is",
        get_application_address(appID),
        "\n",
    )

    # Feeding Func to Algorand blockchain
    def on_msg_globalstate(gs): 

        if gs['state']['Bytes'] == "REQ":
            if gs['reqm']['Bytes'] == "get":

                ackDataFeed(
                    client=client,
                    operator=creator,
                    appID=appID
                )

                method = gs['reqm']['Bytes']
                url = gs['requrl']['Bytes']
                path = gs['path']['Bytes']

                print("Operator sending ... \n http request \n   method=",method, 
                                "\n   url=", url, 
                                "\n   path=", path)
                resp = requests.get(url)
                json_data = json.loads(resp.text)

                jsonpath_expr= parse(path)
                price = jsonpath_expr.find(json_data)

                # Result data from Offchain Data
                respData = price[0].value 

                # Feed data to Algorand blockchain
                updateDataFeed(
                    client=client,
                    operator=creator,
                    appID=appID,
                    respData=bytes(str(respData), 'utf-8'),
                )
                
    # Subscribe Event from Algorand blockchain
    subscriber_run("ws://localhost:1323/ws",
                on_msg_globalstate) 

    sleep(3)

    print(
        "Call \"get ETH/USD price\" to Offchain Contract.\n",
    )       
    # Request ETH/USD DataFeed!
    requestDataFeed(
        client=client,
        operator=creator,
        appID=appID,
        method=b"get",
        url=b"https://min-api.cryptocompare.com/data/pricemultifull?fsyms=ETH&tsyms=USD",
        path=b"RAW.ETH.USD.PRICE"
    )

    waitOffChainAppReadyToRequest(
        client=client,
        appID=appID,
        timeout = 50,
    )

    print("Operator's stored (respdata)")

    # Read Data from Blockchain!
    gs = getAppGlobalState(
            client=client,
            appID=appID)
    
    print("\nOn-chain ETH/USD price is",gs[b"respdata"])
    
    subscriber_exit()
    
demo()


# let parameters = ("get", "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=ETH&tsyms=USD", "path", "RAW.ETH.USD.PRICE", "times", "100000000");
