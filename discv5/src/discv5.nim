import
  random, chronos, sequtils, chronicles, tables, stint, options,
  eth/[keys, rlp, async_utils], eth/p2p/enode, eth/trie/db,
  eth/p2p/discoveryv5/[discovery_db, enr, node, types, routing_table, encoding],
  eth/p2p/discoveryv5/protocol as discv5_protocol,
  ./utils

const N = 100
type
    NodeArray = array[N, discv5_protocol.Protocol]

proc randNode(nodes: NodeArray): Node =
    randomize()
    result = nodes[rand(N - 1)].localNode

proc run() {.async.} =
    var nodes: NodeArray

    for i in 0..<N:
        let node = initDiscoveryNode(newPrivateKey(), localAddress(20300 + i), if i > 0: @[nodes[0].localNode.record] else: @[])
        node.start()
        nodes[i] = node

    echo "Setup ", N, " nodes"

    echo "Sleeping for 50 seconds"
    await sleepAsync(50.seconds)

    let target = randNode(nodes)

    let node = initDiscoveryNode(newPrivateKey(), localAddress(20300 + N), @[nodes[0].localNode.record])

    var peer = randNode(nodes)
    while true:
        let lookup = await node.findNode(peer, 50)
        # @TODO CHECK IF NODE IS IN RETURN
        # @TODO FIND CLOSEST NODE TO OUR TARGET
        # REPEAT
        echo "Found ", lookup.len, " nodes"

when isMainModule:
    waitFor run()
