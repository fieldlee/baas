apt-get -y update && apt-get -y install jq

export ORDERER_CA=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/-DomainForReplace-/orderers/-OrderIdForReplace-.-DomainForReplace-/msp/tlscacerts/tlsca.-DomainForReplace--cert.pem

export CHANNEL_NAME=-ChannelIdForReplace-

echo $ORDERER_CA && echo $CHANNEL_NAME

peer channel fetch config config_block.pb -o -OrderIdForReplace-.-DomainForReplace-:7050 -c -ChannelIdForReplace- --tls --cafile $ORDERER_CA

configtxlator proto_decode --input config_block.pb --type common.Block | jq .data.data[0].payload.data.config > config.json

jq -s '.[0] * {"channel_group":{"groups":{"Application":{"groups": {"-OrgIDForReplace-":.[1]}}}}}' config.json ./channel-artifacts/-OrgIDForReplace-.json > modified_config.json

configtxlator proto_encode --input config.json --type common.Config --output config.pb

configtxlator proto_encode --input modified_config.json --type common.Config --output modified_config.pb

configtxlator compute_update --channel_id -ChannelIdForReplace- --original config.pb --updated modified_config.pb --output -OrgIDForReplace-_update.pb

configtxlator proto_decode --input -OrgIDForReplace-_update.pb --type common.ConfigUpdate | jq . > -OrgIDForReplace-_update.json

echo '{"payload":{"header":{"channel_header":{"channel_id":"-ChannelIdForReplace-", "type":2}},"data":{"config_update":'$(cat -OrgIDForReplace-_update.json)'}}}' | jq . > -OrgIDForReplace-_update_in_envelope.json

configtxlator proto_encode --input -OrgIDForReplace-_update_in_envelope.json --type common.Envelope --output -OrgIDForReplace-_update_in_envelope.pb

peer channel signconfigtx -f -OrgIDForReplace-_update_in_envelope.pb

#export CORE_PEER_LOCALMSPID="Org2MSP"
#
#export CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
#
#export CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
#
#export CORE_PEER_ADDRESS=peer0.org2.example.com:9051

peer channel update -f -OrgIDForReplace-_update_in_envelope.pb -c -ChannelIdForReplace- -o -OrderIdForReplace-.-DomainForReplace-:7050 --tls --cafile $ORDERER_CA
