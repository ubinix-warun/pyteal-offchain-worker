from pyteal import *

def approval_program():
    ocw_state_key = Bytes("state")
    req_method_key = Bytes("reqm")
    req_url_key = Bytes("requrl")
    resp_path_key = Bytes("path")
    resp_data_key = Bytes("respdata")

    on_create = Seq(
        App.globalPut(ocw_state_key, Bytes("IDLE")),
        Approve(),
    )

    on_request_get = Seq(
        App.globalPut(ocw_state_key, Bytes("REQ")),
        App.globalPut(req_method_key, Txn.application_args[0]),
        App.globalPut(req_url_key, Txn.application_args[1]),
        App.globalPut(resp_path_key, Txn.application_args[2]),
        Approve(),
    )

    on_request_ack = Seq(
        App.globalPut(ocw_state_key, Bytes("INPRG")),
        App.globalPut(req_method_key, Bytes("INPRG")),
        App.globalPut(req_url_key, Bytes("INPRG")),
        App.globalPut(resp_path_key, Bytes("INPRG")),
        App.globalPut(resp_data_key, Bytes("0")),
        Approve(),
    )

    on_request_done = Seq(
        App.globalPut(ocw_state_key, Bytes("DONE")),
        App.globalPut(req_method_key, Bytes("IDLE")),
        App.globalPut(req_url_key, Bytes("IDLE")),
        App.globalPut(resp_path_key, Bytes("IDLE")),
        App.globalPut(resp_data_key, Txn.application_args[1]),
        Approve(),
    )

    on_request_method = Txn.application_args[0]
    on_request = Cond(
        [on_request_method == Bytes("get"), on_request_get],
        [on_request_method == Bytes("ack"), on_request_ack],
        [on_request_method == Bytes("done"), on_request_done],
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, on_request],
        [
            Or(
                Txn.on_completion() == OnComplete.OptIn,
                Txn.on_completion() == OnComplete.CloseOut,
                Txn.on_completion() == OnComplete.UpdateApplication,
            ),
            Reject(),
        ],
    )

    return program

def clear_state_program():
    return Approve()

if __name__ == "__main__":
    with open("offchain_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("offchain_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)