from time import time, sleep
from typing import Tuple, List

from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.logic import get_application_address
from algosdk import account, encoding

from pyteal import compileTeal, Mode

from .account import Account
from .contracts import approval_program, clear_state_program
from .util import (
    waitForTransaction,
    fullyCompileContract,
    getAppGlobalState,
)

APPROVAL_PROGRAM = b""
CLEAR_STATE_PROGRAM = b""


def getContracts(client: AlgodClient) -> Tuple[bytes, bytes]:
    """Get the compiled TEAL contracts for the offchain.

    Args:
        client: An algod client that has the ability to compile TEAL programs.

    Returns:
        A tuple of 2 byte strings. The first is the approval program, and the
        second is the clear state program.
    """
    global APPROVAL_PROGRAM
    global CLEAR_STATE_PROGRAM

    if len(APPROVAL_PROGRAM) == 0:
        APPROVAL_PROGRAM = fullyCompileContract(client, approval_program())
        CLEAR_STATE_PROGRAM = fullyCompileContract(client, clear_state_program())

    return APPROVAL_PROGRAM, CLEAR_STATE_PROGRAM


def createOffChainApp(
    client: AlgodClient,
    operator: Account,
) -> int:
    """Create a new offchain.

    Args:
        client: An algod client.
        operator: The account that will create the offchain application.

    Returns:
        The ID of the newly created offchain app.
    """
    approval, clear = getContracts(client)

    globalSchema = transaction.StateSchema(num_uints=0, num_byte_slices=5)
    localSchema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    app_args = [
        # encoding.decode_address(seller),
        # nftID.to_bytes(8, "big"),
        # startTime.to_bytes(8, "big"),
        # endTime.to_bytes(8, "big"),
        # reserve.to_bytes(8, "big"),
        # minBidIncrement.to_bytes(8, "big"),
    ]

    txn = transaction.ApplicationCreateTxn(
        sender=operator.getAddress(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval,
        clear_program=clear,
        global_schema=globalSchema,
        local_schema=localSchema,
        app_args=app_args,
        sp=client.suggested_params(),
    )

    signedTxn = txn.sign(operator.getPrivateKey())

    client.send_transaction(signedTxn)

    response = waitForTransaction(client, signedTxn.get_txid())
    assert response.applicationIndex is not None and response.applicationIndex > 0
    return response.applicationIndex

def waitOffChainAppReadyToRequest(
    client: AlgodClient,
    appID: int,
    timeout: int
) -> None:
    """Wait a new offchain.

    Args:
        client: An algod client.
        appID: The app ID of the offchain.
        timeout: Expire waiting loop in second.
    """

    appAddr = get_application_address(appID)

    currentState = b"NULL"
    count = 0
    for a in range(timeout):
        sleep(1)
        appGlobalState = getAppGlobalState(client, appID)
        count = count + 1
        state = appGlobalState[b"state"]
        if currentState != state:
            print("Operator state [", currentState.decode('UTF-8'),
                     "=>", state.decode('UTF-8'), "] at counter=", str(count) + "s")
            currentState = state

        if currentState == b"DONE":
            break


def requestDataFeed(
    client: AlgodClient,
    operator: Account,
    appID: int,
    method: any,
    url: any,
    path: any,
) -> None:
    """Request the data feed.

    Args:
        client: An algod client.
        operator: The account that will create the offchain application.
        appID: The app ID of the offchain.
        method: "get", etc.
        url: The url used by operator to get data.
        path: Ref. to json data, in JSON path (like xpath)

    """
    approval, clear = getContracts(client)

    app_args = [
        method,
        url,
        path,
    ]

    suggestedParams = client.suggested_params()

    appCallTxn = transaction.ApplicationCallTxn(
        sender=operator.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=app_args,
        sp=suggestedParams,
    )

    signedAppCallTxn = appCallTxn.sign(operator.getPrivateKey())
    client.send_transaction(signedAppCallTxn)

    response = waitForTransaction(client, signedAppCallTxn.get_txid())
    

def ackDataFeed(
    client: AlgodClient,
    operator: Account,
    appID: int,
) -> None:
    """Acknowledge the data feed.

    Args:
        client: An algod client.
        operator: The account that will create the offchain application.
        appID: The app ID of the offchain.

    """
    approval, clear = getContracts(client)

    app_args = [
        b"ack",
    ]

    suggestedParams = client.suggested_params()

    appCallTxn = transaction.ApplicationCallTxn(
        sender=operator.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=app_args,
        sp=suggestedParams,
    )

    signedAppCallTxn = appCallTxn.sign(operator.getPrivateKey())
    client.send_transaction(signedAppCallTxn)

    response = waitForTransaction(client, signedAppCallTxn.get_txid())
    
def updateDataFeed(
    client: AlgodClient,
    operator: Account,
    appID: int,
    respData: str,
) -> None:
    """update the data feed.

    Args:
        client: An algod client.
        operator: The account that will create the offchain application.
        appID: The app ID of the offchain.
        respData: Stored data.

    """
    approval, clear = getContracts(client)

    app_args = [
        b"done",
        respData
    ]

    suggestedParams = client.suggested_params()

    appCallTxn = transaction.ApplicationCallTxn(
        sender=operator.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=app_args,
        sp=suggestedParams,
    )

    signedAppCallTxn = appCallTxn.sign(operator.getPrivateKey())
    client.send_transaction(signedAppCallTxn)

    response = waitForTransaction(client, signedAppCallTxn.get_txid())
    