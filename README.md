# PyTEAL Offchain Worker

PyTEAL Offchain Worker with Algorand Indexer (PubSub Event)


# Quickstart

* Create sandbox docker, algod and indexer.

```
./sandbox up -v
Pulling sandbox... (POC: Block PubSub Event)
...
Checkout sandbox... (Branch: Block PubSub Event)
Branch 'block-pubsub' set up to track remote branch 'block-pubsub' from 'origin'.
Switched to a new branch 'block-pubsub'
...

algod version
12885426176
3.8.0.stable [rel/stable] (commit #d867a094)
go-algorand is licensed with AGPLv3.0
source code available at https://github.com/algorand/go-algorand

Indexer version
2.12.3-dev.unknown compiled at 2022-07-08T09:12:22+0000 from git hash 9bd1284f5413cfa032dfa54f7f34451a5716d250 (modified)

Postgres version
postgres (PostgreSQL) 13.7
...

```

* Setup python env.

```
python3 -m venv venv
. venv/bin/activate

pip3 install -r requirements.txt
```

* Run demo script.

```
python3 demo.py 

Generating temporary accounts...
offchain creator account:  NCA5LCK7HQD35PNEMACJ2M76KPTGWWDEAXHPPATB7LCVOIM5QVSCLZVEAU
Done. The OffChain app ID is 17 
and the offchain account is QUT2ZXGAS7AGEW2Z5OIXRK2WZNLZ3FZMWMJDRAN7ESRI32U67SLYB3HDXE 

Subscriber's connected to ws://localhost:1323/ws 

Call "get ETH/USD price" to Offchain Contract.

Operator state [ NULL => REQ ] at counter= 1s
Operator state [ REQ => INPRG ] at counter= 12s
Operator sending ... 
 http request 
   method= get 
   url= https://min-api.cryptocompare.com/data/pricemultifull?fsyms=ETH&tsyms=USD 
   path= RAW.ETH.USD.PRICE
Operator state [ INPRG => DONE ] at counter= 20s
Operator's stored (respdata)

On-chain ETH/USD price is b'1204.7'

```


# Credit

* [Algorand](https://developer.algorand.org/) - Building trusted infrastructure for the Borderless economy. 
* [PyTEAL](https://developer.algorand.org/docs/get-details/dapps/pyteal/) - The python library for generating TEAL programs that provides a convenient and familiar syntax.
* [chainlink-polkadot](https://github.com/smartcontractkit/chainlink-polkadot/tree/master/pallet-chainlink) - This pallet allows your substrate built parachain/blockchain to interract with chainlink. 
* [auction-demo](https://github.com/algorand/auction-demo/) - This demo is an on-chain NFT auction using smart contracts on the Algorand blockchain.

